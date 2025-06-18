import chromadb
from datetime import datetime
from config.settings import CHROMA_DB_DIR
from typing import Dict, List, Optional
import uuid

class VersionManager:
    def __init__(self):
        # Initialize ChromaDB persistent client (new API)
        self.client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
        # Create or get the collection
        self.collection = self.client.get_or_create_collection("content_versions")

    def store_version(self, content: str, metadata: Dict) -> str:
        """Store a new version of content with metadata."""
        version_id = str(uuid.uuid4())
        # Add timestamp if not provided
        if "timestamp" not in metadata:
            metadata["timestamp"] = datetime.now().isoformat()
        self.collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[version_id]
        )
        return version_id

    def get_version(self, version_id: str) -> Optional[Dict]:
        """Retrieve a specific version by ID."""
        try:
            result = self.collection.get(ids=[version_id])
            if result and result["documents"]:
                return {
                    "content": result["documents"][0],
                    "metadata": result["metadatas"][0],
                    "id": version_id
                }
            return None
        except Exception as e:
            print(f"Error retrieving version: {e}")
            return None

    def get_versions_by_metadata(self, metadata_filter: Dict) -> List[Dict]:
        """Retrieve versions matching specific metadata criteria."""
        try:
            results = self.collection.get(
                where=metadata_filter,
                include=["documents", "metadatas"]
            )
            versions = []
            for i in range(len(results["ids"])):
                versions.append({
                    "id": results["ids"][i],
                    "content": results["documents"][i],
                    "metadata": results["metadatas"][i]
                })
            return versions
        except Exception as e:
            print(f"Error querying versions: {e}")
            return []

    def get_latest_version(self, original_url: str) -> Optional[Dict]:
        """Get the most recent version for a given original URL."""
        try:
            # Get all versions for this URL, sorted by timestamp
            versions = self.get_versions_by_metadata({"original_url": original_url})
            if not versions:
                return None
            # Sort by timestamp (newest first)
            versions.sort(
                key=lambda v: v["metadata"].get("timestamp", ""),
                reverse=True
            )
            return versions[0]
        except Exception as e:
            print(f"Error getting latest version: {e}")
            return None

    def get_final_versions(self) -> List[Dict]:
        """Get all versions marked as 'final'."""
        return self.get_versions_by_metadata({"stage": "final"}) 