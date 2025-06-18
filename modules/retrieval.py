from modules.version_manager import VersionManager
from typing import Dict, Optional

class ContentRetriever:
    def __init__(self):
        self.version_manager = VersionManager()

    def retrieve_content(self, criteria: Dict) -> Optional[Dict]:
        """
        Retrieve content based on specified criteria.
        Criteria can include:
        - version_id: Specific version ID
        - original_url: URL of original content
        - stage: Processing stage (raw, AI_spun, human_reviewed, final)
        - latest: Boolean to get latest version
        - final: Boolean to get final versions only
        """
        if "version_id" in criteria:
            return self.version_manager.get_version(criteria["version_id"])
        if criteria.get("final", False):
            return self._select_from_results(self.version_manager.get_final_versions())
        if "original_url" in criteria:
            if criteria.get("latest", False):
                return self.version_manager.get_latest_version(criteria["original_url"])
            else:
                versions = self.version_manager.get_versions_by_metadata(
                    {"original_url": criteria["original_url"]}
                )
                return self._select_from_results(versions)
        if "stage" in criteria:
            versions = self.version_manager.get_versions_by_metadata(
                {"stage": criteria["stage"]}
            )
            return self._select_from_results(versions)
        return None

    def _select_from_results(self, versions: list) -> Optional[Dict]:
        """Select a version from a list of results (simple implementation)."""
        if not versions:
            return None
        # Simple strategy: return the most recent version
        versions.sort(
            key=lambda v: v["metadata"].get("timestamp", ""),
            reverse=True
        )
        return versions[0] 