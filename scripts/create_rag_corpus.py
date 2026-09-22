import vertexai
from vertexai.preview import rag
from vertexai.preview.rag.utils import resources as rr

PROJECT_ID = "qwiklabs-gcp-02-bac4296bfb63"
LOCATION = "us-central1"  # Serverless RAG mode is us-central1 only
GCS_PATH = "gs://smart-plant-assistant-assets-bac4296b/rag/pg22484.txt"

PARSING_PROMPT = (
    "Extract the individual useful facts, plant specs, care instructions, and botanical information described in this text. "
    "Ignore and omit all metadata, Gutenberg boilerplate, and publication info. "
    "Output clean, self-contained prose."
)

print(f"Initializing Vertex AI for project {PROJECT_ID} in {LOCATION}...")
vertexai.init(project=PROJECT_ID, location=LOCATION)

# 1. Switch region's RAG managed DB to serverless mode (project-level, once).
cfg = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
try:
    print("Setting RAG engine config to serverless mode...")
    rag.update_rag_engine_config(
        rag_engine_config=rag.RagEngineConfig(
            name=cfg,
            rag_managed_db_config=rag.RagManagedDbConfig(mode=rr.Serverless()),
        )
    )
    print("Serverless RAG engine config set.")
except Exception as e:
    print(f"Note/Warning on update_rag_engine_config: {e}")

# 2. Create the corpus.
print("Creating RAG corpus 'smart-plant-assistant-rag'...")
corpus = rag.create_corpus(
    display_name="smart-plant-assistant-rag",
    embedding_model_config=rag.EmbeddingModelConfig(
        publisher_model="publishers/google/models/text-embedding-005"
    ),
)
print("CREATED CORPUS NAME:", corpus.name)

# 3. Import + parse + chunk + embed.
print(f"Importing and indexing {GCS_PATH} into corpus...")
resp = rag.import_files(
    corpus_name=corpus.name,
    paths=[GCS_PATH],
    transformation_config=rag.TransformationConfig(
        chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
    ),
    llm_parser=rag.LlmParserConfig(
        model_name="gemini-2.5-flash",
        custom_parsing_prompt=PARSING_PROMPT,
    ),
)
print("Import complete! Imported files count:", getattr(resp, "imported_rag_files_count", "N/A"))

# Write corpus name to a local file for tool reference
with open("data/rag_corpus_info.txt", "w") as f:
    f.write(corpus.name.strip())

print(f"Saved corpus resource name '{corpus.name}' to data/rag_corpus_info.txt")
