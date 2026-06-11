from langchain_chroma import Chroma
from llm_config import get_embeddings

class BlogMemory:
    """
    Manages the persistent storage and retrieval of blog history and academic references.
    """
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.embeddings = get_embeddings()
        self.vectorstore = Chroma(
            collection_name="blog_history",
            embedding_function=self.embeddings,
            persist_directory=persist_directory
        )
        # Rename/Ensure collection name is 'reference_library'
        self.ref_store = Chroma(
            collection_name="reference_library",
            embedding_function=self.embeddings,
            persist_directory=persist_directory
        )

    def get_recent_summaries(self, limit: int = 5) -> str:
        """
        Retrieves the most recent blog titles and summaries without a vector search.
        Saves quota by avoiding embedding calls.
        """
        try:
            results = self.vectorstore.get()
            if not results or not results['metadatas']:
                return "No previous history found."
            
            # Get the most recent entries
            recent = results['metadatas'][-limit:]
            context = []
            for m in recent:
                title = m.get('title', 'Untitled')
                summary = m.get('summary', 'No summary available')
                context.append(f"Title: {title}\nSummary: {summary}")
            
            return "\n\n".join(context)
        except Exception as e:
            return f"Error retrieving recent summaries: {e}"

    def search_history(self, topic: str, k: int = 10) -> str:
        """
        Searches history using vector similarity, limited to top k (max 10). 
        Returns only Title and Summary to save tokens.
        """
        try:
            results = self.vectorstore.similarity_search(topic, k=min(k, 10))
            if not results:
                return "No related previous history found."
            
            summaries = []
            for doc in results:
                title = doc.metadata.get('title', 'Untitled')
                summary = doc.metadata.get('summary', 'No summary available')
                summaries.append(f"Title: {title}\nSummary: {summary}")
            return "\n\n".join(summaries)
        except Exception as e:
            return f"Error searching history: {e}"

    def save_blog(self, title: str, content: str, short_summary: str):
        """
        Saves the full blog content and the 4-5 line summary to ChromaDB.
        """
        self.vectorstore.add_texts(
            texts=[content],
            metadatas=[{"title": title, "summary": short_summary}]
        )
        print(f"--- Blog Saved: {title} ---")

    def save_references(self, blog_title: str, refs_list: list[dict]):
        """
        Stores academic references linked to a specific blog post.
        """
        if not refs_list:
            return
            
        texts = [f"{r.get('title')} by {r.get('author')}" for r in refs_list]
        metadatas = [{"blog_link": blog_title, **r} for r in refs_list]
        
        self.ref_store.add_texts(texts=texts, metadatas=metadatas)
        print(f"--- Saved {len(refs_list)} references for: {blog_title} ---")

    def get_reference_context(self, limit: int = 5) -> str:
        """
        Retrieves a summary of the most recently cited authors and papers to help discovery.
        """
        try:
            results = self.ref_store.get()
            if not results or not results['metadatas']:
                return "No papers in the reference library yet."
            
            # Get the most recent entries
            recent_refs = results['metadatas'][-limit:]
            context = []
            for r in recent_refs:
                context.append(f"- {r.get('title')} ({r.get('author')}) [Cited in: {r.get('blog_link')}]")
            
            return "\n".join(context)
        except Exception as e:
            return f"Error retrieving reference context: {e}"
