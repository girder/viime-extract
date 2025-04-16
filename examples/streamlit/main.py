import io
from pathlib import Path
import tempfile
import tomllib
import json

import streamlit as st
from streamlit_layoutr import streamlit_layoutr
from st_keyup import st_keyup

import dotenv
from langchain_openai import ChatOpenAI

from viime_extract.extract import extract_article_from_document_loader
from viime_extract.config import Config
from viime_extract.schema import Article


def article_to_graph(data: Article):
    metabolites = set()
    proteins = set()
    genes = set()
    pathways = set()
    drugs = set()
    diseases = set()
    authors = set()

    nodes = []
    links = []

    total_metabolites = 0
    total_proteins = 0
    total_genes = 0
    total_pathways = 0
    total_drugs = 0
    total_diseases = 0
    total_authors = 0

    paper_id = data.meta.title
    nodes.append({"id": paper_id, "type": "paper"})

    keywords = data.keywords
    total_metabolites += len(keywords.mentioned_metabolites)
    for m in [d for d in keywords.mentioned_metabolites if d.name.lower() != "unknown"]:
        name = m.name.lower() + " metabolite"
        if name not in metabolites:
            metabolites.add(name)
            nodes.append({"id": name, "type": "metabolite"})
        links.append([paper_id, name])
    total_proteins += len(keywords.mentioned_proteins)
    for p in [d for d in keywords.mentioned_proteins if d.name.lower() != "unknown"]:
        name = p.name.lower() + " protein"
        if name not in proteins:
            proteins.add(name)
            nodes.append({"id": name, "type": "protein"})
        links.append([paper_id, name])
    total_genes += len(keywords.mentioned_genes)
    for g in [d for d in keywords.mentioned_genes if d.name.lower() != "unknown"]:
        name = g.name.lower() + " gene"
        if name not in genes:
            genes.add(name)
            nodes.append({"id": name, "type": "gene"})
        links.append([paper_id, name])
    total_pathways += len(keywords.mentioned_pathways)
    for p in [d for d in keywords.mentioned_pathways if d.name.lower() != "unknown"]:
        name = p.name.lower() + " pathway"
        if name not in pathways:
            pathways.add(name)
            nodes.append({"id": name, "type": "pathway"})
        links.append([paper_id, name])
    total_drugs += len(keywords.mentioned_drugs)
    for d in [d for d in keywords.mentioned_drugs if d.name.lower() != "unknown"]:
        name = d.name.lower() + " drug"
        if name not in drugs:
            drugs.add(name)
            nodes.append({"id": name, "type": "drug"})
        links.append([paper_id, name])
    total_diseases += len(keywords.mentioned_diseases)
    for d in [d for d in keywords.mentioned_diseases if d.name.lower() != "unknown"]:
        name = d.name.lower() + " disease"
        if name not in diseases and name != "unknown":
            diseases.add(name)
            nodes.append({"id": name, "type": "disease"})
        links.append([paper_id, name])
    total_authors += len(data.meta.authors)
    for a in data.meta.authors:
        name = f"{a.firstname} {a.surname}"
        if name not in authors:
            authors.add(name)
            nodes.append({"id": name, "type": "author"})
        links.append([paper_id, name])
    return {"nodes": nodes, "links": links}


dotenv.load_dotenv()

st.set_page_config(layout="wide")


@st.cache_data
def process_article(pdf_bytes):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
        temp_pdf.write(pdf_bytes)
        temp_pdf.flush()
        config_path = Path(__file__).parent / "viime-extract-config.toml"
        with open(config_path, "rb") as fp:
            config = Config.model_validate(tomllib.load(fp))
        # model = ChatOpenAI(model=config.model_name, temperature=config.temperature)
        model = ChatOpenAI(model=config.model_name)
        article_extraction = extract_article_from_document_loader(
            doc_loader=config.pdf_loader.create_loader(temp_pdf.name),
            model=model,
            splitter=config.text_splitter.create_splitter(),
            detect_references_prompt=config.prompts.detect_references,
            article_metadata_prompt=config.prompts.article_metadata,
            article_keywords_prompt=config.prompts.article_keywords,
            without_references=config.extractor.without_references,
        )
        return article_extraction


@st.cache_data
def process_json(json_bytes):
    article_data = json.loads(json_bytes)
    return Article(**article_data)


def merge_graphs(graph1, graph2):
    existing_node_ids = {node["id"] for node in graph1["nodes"]}
    nodes = graph1["nodes"] + [
        node for node in graph2["nodes"] if node["id"] not in existing_node_ids
    ]
    links = graph1["links"] + graph2["links"]
    return {"nodes": nodes, "links": links}


@st.cache_data
def build_article_graph(article_jsons, article_pdfs):
    article_graph = {"nodes": [], "links": []}

    if article_jsons:
        for starting_graph in article_jsons:
            article_data = process_json(starting_graph)
            cur_graph = article_to_graph(article_data)
            article_graph = merge_graphs(article_graph, cur_graph)

    if article_pdfs:
        for article in article_pdfs:
            article_data = process_article(article)
            st.json(article_data.model_dump_json(indent=2), expanded=False)
            cur_graph = article_to_graph(article_data)
            article_graph = merge_graphs(article_graph, cur_graph)

    # compute "count" property on each node, which is the degree of the node
    for node in article_graph["nodes"]:
        node["count"] = 0
    for link in article_graph["links"]:
        for node in article_graph["nodes"]:
            if node["id"] == link[0]:
                node["count"] += 1
            if node["id"] == link[1]:
                node["count"] += 1
    return article_graph


article_jsons_files = st.file_uploader("Article JSONs", accept_multiple_files=True)
article_jsons = (
    [] if article_jsons_files is None else [d.getvalue() for d in article_jsons_files]
)

article_pdfs_files = st.file_uploader("Article PDFs", accept_multiple_files=True)
article_pdfs = (
    [] if article_pdfs_files is None else [d.getvalue() for d in article_pdfs_files]
)

article_graph = build_article_graph(article_jsons, article_pdfs)


def subgraph(node_filter):
    filtered_nodes = [node for node in article_graph["nodes"] if node_filter(node)]
    filtered_node_ids = {node["id"] for node in filtered_nodes}
    filtered_links = [
        link
        for link in article_graph["links"]
        if link[0] in filtered_node_ids and link[1] in filtered_node_ids
    ]
    return {"nodes": filtered_nodes, "links": filtered_links}


count_min = st.sidebar.slider("Minimum node connections", 0, 100, 1)

if count_min > 0:
    article_graph = subgraph(lambda node: node["count"] >= count_min)

d3_category_10 = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]

type_colors = {
    "paper": d3_category_10[0],
    "metabolite": d3_category_10[1],
    "protein": d3_category_10[2],
    "gene": d3_category_10[3],
    "pathway": d3_category_10[4],
    "drug": d3_category_10[5],
    "disease": d3_category_10[6],
    "author": d3_category_10[7],
}


def render_legend():
    enabled_set = set()
    for type_name, color in type_colors.items():
        st.sidebar.markdown(
            f"<style>"
            f'.{f"st-key-toggle_{type_name}"} span {{ background-color: {color}; border-color: {color}; }}'
            f"</style>",
            unsafe_allow_html=True,
        )
        type_count = len([n for n in article_graph["nodes"] if n["type"] == type_name])
        enabled = st.sidebar.checkbox(
            f"{type_name.capitalize()} ({type_count})",
            value=True,
            key=f"toggle_{type_name}",
        )
        if enabled:
            enabled_set.add(type_name)
    return enabled_set


enabled_types = render_legend()
node_filter = lambda node: node["type"] in enabled_types
article_graph = subgraph(node_filter)

search = st.text_input("Search")
if search and len(search.strip()) > 0:
    search = search.strip().lower()
    node_filter = lambda node: search in node["id"].lower()
    article_graph = subgraph(node_filter)

for n in article_graph["nodes"]:
    n["color"] = type_colors[n["type"]]

with st.sidebar:
    run_layout = st.toggle("Run layout", True)
    node_size = st.slider("Node size", 0.0, 0.1, 0.05, 0.001)
    node_size_field = st.selectbox("Node size field", options=["degree", None])
    node_color_field = st.selectbox("Node color field", options=["color", "type", None])
    node_color_mode = "identity" if node_color_field == "color" else "auto"
    node_opacity = st.slider("Node opacity", 0.0, 1.0, 1.0, 0.01)
    node_stroke_width = st.slider("Node stroke width", 0.0, 10.0, 1.0, 0.01)
    node_stroke_opacity = st.slider("Node stroke opacity", 0.0, 1.0, 1.0, 0.01)
    node_label_field = st.selectbox(
        "Node label field", options=["label", "id", "type", None]
    )
    node_label_max_count = st.slider(
        "Node label max count (0 for no limit)", 0, 1000, 100
    )
    node_label_font_size = st.slider("Node label font size", 0.0, 100.0, 12.0, 0.01)
    node_label_max_length = st.slider(
        "Node label max length (0 for no limit)", 1, 100, 12, 1
    )
    link_width = st.slider("Link width", 0.0, 10.0, 2.0, 0.01)
    link_opacity = st.slider("Link opacity", 0.0, 1.0, 0.05, 0.01)

    energy = st.slider("Energy", 0.0, 1.0, 1.0, 0.01)
    collide_strength = st.slider("Collide strength", 0.0, 1.0, 1.0, 0.01)
    charge_strength = st.slider("Charge strength", 0.0, 1.0, 1.0, 0.01)
    charge_approximation = st.slider("Charge approximation", 0.0, 1.0, 1.0, 0.01)
    link_strength = st.slider("Link strength", 0.0, 0.1, 0.05, 0.001)
    gravity_strength = st.slider("Gravity strength", 0.0, 0.1, 0.01, 0.001)
    center_strength = st.slider("Center strength", 0.0, 1.0, 1.0, 0.01)

article_graph["nodes"] = [
    {**node, "label": node["id"][:node_label_max_length]}
    for node in article_graph["nodes"]
]

graph_string = json.dumps(article_graph)

output = streamlit_layoutr(
    graph=graph_string,
    run_layout=run_layout,
    node_size=node_size,
    node_size_field=node_size_field,
    node_color_field=node_color_field,
    node_color_mode=node_color_mode,
    node_opacity=node_opacity,
    node_stroke_width=node_stroke_width,
    node_stroke_opacity=node_stroke_opacity,
    node_label_field=node_label_field,
    node_label_max_count=node_label_max_count,
    node_label_font_size=node_label_font_size,
    link_width=link_width,
    link_opacity=link_opacity,
    energy=energy,
    collide_strength=collide_strength,
    charge_strength=charge_strength,
    charge_approximation=charge_approximation,
    link_strength=link_strength,
    gravity_strength=gravity_strength,
    center_strength=center_strength,
    key="a",
)

hovered = st.empty()
selected = st.empty()

node = output.get("hovered")
if node:
    hovered.markdown(f"Hovered node: {node.get('id')}, Type: {node.get('type')}")

select = output.get("selected")
if select:
    selected.markdown(f"Selected node: {select.get('id')}, Type: {select.get('type')}")

dataset_name = st_keyup("Dataset name", value="graph")
file_name = f"{dataset_name}.json"
st.download_button(
    label=f"Download Graph as {file_name}",
    data=graph_string,
    file_name=file_name,
    mime="application/json",
)
