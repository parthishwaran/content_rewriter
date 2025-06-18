import os
from pathlib import Path
from datetime import datetime
from modules.scraper import WebScraper
from modules.ai_processor import AIProcessor
from modules.human_interface import HumanInterface
from modules.version_manager import VersionManager
from modules.retrieval import ContentRetriever
from config.settings import RAW_CONTENT_DIR, PROCESSED_CONTENT_DIR

class ContentRewriterApp:
    def __init__(self):
        self.scraper = WebScraper()
        self.ai_processor = AIProcessor()
        self.human_interface = HumanInterface()
        self.version_manager = VersionManager()
        self.retriever = ContentRetriever()

    def run(self):
        """Main application loop."""
        print("\n=== Automated Book Reviewer System ===")
        while True:
            choice = self.human_interface.get_user_choice(
                "\nMain Menu:",
                [
                    "Scrape and process new content",
                    "Continue processing existing content",
                    "Retrieve and view previous versions",
                    "Exit"
                ]
            )
            if choice == 1:
                self.process_new_content()
            elif choice == 2:
                self.continue_processing()
            elif choice == 3:
                self.retrieve_versions()
            elif choice == 4:
                print("Exiting the application.")
                break
        self.scraper.close()

    def process_new_content(self):
        """Process new content from a URL."""
        url = self.human_interface.get_human_input(
            "Enter the URL to scrape"
            # "https://en.wikisource.org/wiki/The_Gates_of_Morning/Book_1/Chapter_1"
        )
        chapter_title = self.human_interface.get_human_input(
            "Enter the chapter title to extract",
            # "Chapter 1"
        )
        print("\nScraping content...")
        scraped_data = self.scraper.scrape_content(url, chapter_title)
        if not scraped_data or not scraped_data["content"]:
            print("Failed to scrape content.")
            return
        # Store raw version
        raw_metadata = {
            "original_url": url,
            "chapter_title": chapter_title,
            "stage": "raw",
            "processed_by": "scraper",
            "timestamp": datetime.now().isoformat()
        }
        raw_version_id = self.version_manager.store_version(
            scraped_data["content"],
            raw_metadata
        )
        print(f"\nScraped content saved as version ID: {raw_version_id}")
        # Proceed with AI processing
        self.ai_processing_workflow(scraped_data["content"], url, chapter_title, raw_version_id)

    def ai_processing_workflow(self, original_content, url, chapter_title, source_version_id):
        """Handle the AI processing workflow."""
        print("\nStarting AI processing...")
        # AI Rewriting
        print("\nAI is rewriting the content...")
        ai_rewritten = self.ai_processor.rewrite_content(original_content)
        if not ai_rewritten:
            print("AI rewriting failed.")
            return
        # Store AI-spun version
        ai_metadata = {
            "original_url": url,
            "chapter_title": chapter_title,
            "stage": "AI_spun",
            "processed_by": "AI Writer",
            "source_version": source_version_id,
            "timestamp": datetime.now().isoformat()
        }
        ai_version_id = self.version_manager.store_version(ai_rewritten, ai_metadata)
        print(f"AI-rewritten content saved as version ID: {ai_version_id}")
        # AI Review
        print("\nAI is reviewing the rewritten content...")
        ai_reviewed = self.ai_processor.review_content(ai_rewritten)
        if not ai_reviewed:
            print("AI review failed.")
            return
        # Store AI-reviewed version
        reviewed_metadata = {
            "original_url": url,
            "chapter_title": chapter_title,
            "stage": "AI_reviewed",
            "processed_by": "AI Reviewer",
            "source_version": ai_version_id,
            "timestamp": datetime.now().isoformat()
        }
        reviewed_version_id = self.version_manager.store_version(ai_reviewed, reviewed_metadata)
        print(f"AI-reviewed content saved as version ID: {reviewed_version_id}")
        # Show differences
        self.human_interface.display_content_differences(
            ai_rewritten,
            ai_reviewed,
            "AI Rewritten",
            "AI Reviewed"
        )
        # Proceed to human review
        self.human_review_workflow(ai_reviewed, url, chapter_title, reviewed_version_id)

    def human_review_workflow(self, content, url, chapter_title, source_version_id):
        """Handle the human review workflow."""
        print("\nStarting human review process...")
        # Human Writer review
        print("\nHuman Writer Review:")
        print("The AI-reviewed content will be opened in an editor for your modifications.")
        edited_content = self.human_interface.edit_content_in_editor(content)
        if edited_content is None:
            print("No changes made by Human Writer.")
            human_writer_version_id = source_version_id
        else:
            # Store Human Writer version
            writer_metadata = {
                "original_url": url,
                "chapter_title": chapter_title,
                "stage": "human_writer_reviewed",
                "processed_by": "Human Writer",
                "source_version": source_version_id,
                "timestamp": datetime.now().isoformat()
            }
            human_writer_version_id = self.version_manager.store_version(
                edited_content,
                writer_metadata
            )
            print(f"Human Writer version saved as ID: {human_writer_version_id}")
            # Show differences
            self.human_interface.display_content_differences(
                content,
                edited_content,
                "AI Reviewed",
                "Human Writer Edited"
            )
            content = edited_content
        # Human Reviewer
        print("\nHuman Reviewer Stage:")
        print("The content will be opened again for final review.")
        reviewed_content = self.human_interface.edit_content_in_editor(content)
        if reviewed_content is None:
            print("No changes made by Human Reviewer.")
            human_reviewer_version_id = human_writer_version_id
        else:
            # Store Human Reviewer version
            reviewer_metadata = {
                "original_url": url,
                "chapter_title": chapter_title,
                "stage": "human_reviewed",
                "processed_by": "Human Reviewer",
                "source_version": human_writer_version_id,
                "timestamp": datetime.now().isoformat()
            }
            human_reviewer_version_id = self.version_manager.store_version(
                reviewed_content,
                reviewer_metadata
            )
            print(f"Human Reviewer version saved as ID: {human_reviewer_version_id}")
            # Show differences if there were changes
            if reviewed_content != content:
                self.human_interface.display_content_differences(
                    content,
                    reviewed_content,
                    "Previous Version",
                    "Human Reviewed"
                )
            content = reviewed_content
        # Final Editor
        print("\nFinal Editor Stage:")
        print("Please make any final edits before marking as complete.")
        final_content = self.human_interface.edit_content_in_editor(content)
        if final_content is None:
            print("No changes made by Final Editor.")
            final_version_id = human_reviewer_version_id
        else:
            # Store final version
            final_metadata = {
                "original_url": url,
                "chapter_title": chapter_title,
                "stage": "final",
                "processed_by": "Final Editor",
                "source_version": human_reviewer_version_id,
                "timestamp": datetime.now().isoformat()
            }
            final_version_id = self.version_manager.store_version(
                final_content,
                final_metadata
            )
            print(f"Final version saved as ID: {final_version_id}")
            # Show differences if there were changes
            if final_content != content:
                self.human_interface.display_content_differences(
                    content,
                    final_content,
                    "Reviewed Version",
                    "Final Version"
                )
        print("\nContent processing complete!")
        print(f"Final version ID: {final_version_id}")

    def continue_processing(self):
        """Continue processing an existing content version."""
        url = self.human_interface.get_human_input("Enter the original URL of the content:")
        # Get latest version for this URL
        latest_version = self.retriever.retrieve_content({
            "original_url": url,
            "latest": True
        })
        if not latest_version:
            print("No versions found for this URL.")
            return
        print(f"\nLatest version found (ID: {latest_version['id']}):")
        print(f"Stage: {latest_version['metadata']['stage']}")
        print(f"Last processed by: {latest_version['metadata']['processed_by']}")
        print(f"Timestamp: {latest_version['metadata']['timestamp']}")
        # Determine where to continue processing
        stage = latest_version['metadata']['stage']
        if stage == "raw":
            self.ai_processing_workflow(
                latest_version['content'],
                url,
                latest_version['metadata'].get('chapter_title', 'Unknown'),
                latest_version['id']
            )
        elif stage in ["AI_spun", "AI_reviewed"]:
            self.human_review_workflow(
                latest_version['content'],
                url,
                latest_version['metadata'].get('chapter_title', 'Unknown'),
                latest_version['id']
            )
        elif stage in ["human_writer_reviewed", "human_reviewed"]:
            # We'll treat both as starting at human review stage
            self.human_review_workflow(
                latest_version['content'],
                url,
                latest_version['metadata'].get('chapter_title', 'Unknown'),
                latest_version['id']
            )
        elif stage == "final":
            print("This content has already been finalized.")

    def retrieve_versions(self):
        """Retrieve and display previous versions."""
        url = self.human_interface.get_human_input("Enter the original URL of the content (leave blank for all):")
        if url.strip():
            versions = self.version_manager.get_versions_by_metadata({"original_url": url})
        else:
            # Get all versions
            versions = []
            results = self.version_manager.collection.get()
            for i in range(len(results["ids"])):
                versions.append({
                    "id": results["ids"][i],
                    "content": results["documents"][i],
                    "metadata": results["metadatas"][i]
                })
        if not versions:
            print("No versions found.")
            return
        # Sort by timestamp (newest first)
        versions.sort(
            key=lambda v: v["metadata"].get("timestamp", ""),
            reverse=True
        )
        print("\nAvailable versions:")
        for i, version in enumerate(versions, 1):
            print(f"{i}. ID: {version['id']}")
            print(f"   Stage: {version['metadata']['stage']}")
            print(f"   Processed by: {version['metadata']['processed_by']}")
            print(f"   Timestamp: {version['metadata']['timestamp']}")
            print()
        # Let user select a version to view
        choice = self.human_interface.get_user_choice(
            "Select a version to view (or 0 to cancel):",
            [v['id'] for v in versions]
        )
        if choice == 0:
            return
        selected_version = versions[choice - 1]
        print(f"\n=== Content for version {selected_version['id']} ===")
        print(f"Stage: {selected_version['metadata']['stage']}")
        print(f"Processed by: {selected_version['metadata']['processed_by']}")
        print(f"Timestamp: {selected_version['metadata']['timestamp']}")
        print("\nContent:")
        print(selected_version['content'][:1000] + ("..." if len(selected_version['content']) > 1000 else ""))
        # Option to see full content
        see_full = self.human_interface.get_human_input("\nView full content? (y/n)", "n").lower()
        if see_full == 'y':
            print("\n=== FULL CONTENT ===")
            print(selected_version['content'])
        # Option to open in editor
        edit = self.human_interface.get_human_input("\nOpen in editor for modifications? (y/n)", "n").lower()
        if edit == 'y':
            edited_content = self.human_interface.edit_content_in_editor(selected_version['content'])
            if edited_content and edited_content != selected_version['content']:
                # Create new version based on this one
                new_metadata = selected_version['metadata'].copy()
                new_metadata.update({
                    "stage": f"edited_from_{new_metadata['stage']}",
                    "processed_by": "Human Editor",
                    "source_version": selected_version['id'],
                    "timestamp": datetime.now().isoformat()
                })
                new_version_id = self.version_manager.store_version(
                    edited_content,
                    new_metadata
                )
                print(f"\nNew version saved as ID: {new_version_id}")

if __name__ == "__main__":
    app = ContentRewriterApp()
    app.run()
