from .models import SessionLocal, FileMetadata
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.session = SessionLocal()

    def add_or_update_metadata(self, file_path, metadata_dict):
        """Add or update metadata for a file"""
        try:
            # Check if entry exists
            metadata = self.session.query(FileMetadata).filter_by(
                file_path=file_path).first()
            
            if metadata is None:
                metadata = FileMetadata(file_path=file_path)

            # Update fields
            for key, value in metadata_dict.items():
                setattr(metadata, key, value)

            if metadata not in self.session:
                self.session.add(metadata)
                
            self.session.commit()
            return True
        except Exception as e:
            print(f"Error saving metadata: {e}")
            self.session.rollback()
            return False

    def get_metadata(self, file_path):
        """Retrieve metadata for a file"""
        try:
            metadata = self.session.query(FileMetadata).filter_by(
                file_path=file_path).first()
            if metadata:
                return {
                    'project_number': metadata.project_number,
                    'department': metadata.department,
                    'revision': metadata.revision,
                    'type': metadata.type,
                    'area': metadata.area,
                    'progress': metadata.progress,
                    'notes': metadata.notes
                }
            return None
        except Exception as e:
            print(f"Error retrieving metadata: {e}")
            return None

    def __del__(self):
        """Close the session when object is destroyed"""
        self.session.close()