"""Tests for whiteboard search functionality."""
import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.models.user import User
from app.models.whiteboard import Whiteboard
from app.models.collaborator import WhiteboardCollaborator, Permission


class TestWhiteboardSearch:
    """Test whiteboard search API endpoints."""
    
    def test_search_whiteboards_by_title(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        """Test searching whiteboards by title."""
        # Create test whiteboards
        wb1 = Whiteboard(
            title="Python Tutorial Board",
            description="A board for learning Python",
            owner_id=test_user.id
        )
        wb2 = Whiteboard(
            title="JavaScript Guide",
            description="A board for JavaScript tutorials",
            owner_id=test_user.id
        )
        wb3 = Whiteboard(
            title="Data Science Project",
            description="Board for data analysis with Python",
            owner_id=test_user.id
        )
        
        db.add_all([wb1, wb2, wb3])
        db.commit()
        
        # Search for "Python"
        response = client.get(
            "/api/v1/whiteboards/",
            headers=auth_headers,
            params={"search": "Python"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Should find wb1 and wb3
        titles = [wb["title"] for wb in data]
        assert "Python Tutorial Board" in titles
        assert "Data Science Project" in titles
        assert "JavaScript Guide" not in titles
    
    def test_search_whiteboards_by_description(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        """Test searching whiteboards by description."""
        # Create test whiteboards
        wb1 = Whiteboard(
            title="Board 1",
            description="Learning advanced Python concepts",
            owner_id=test_user.id
        )
        wb2 = Whiteboard(
            title="Board 2",
            description="Basic HTML and CSS",
            owner_id=test_user.id
        )
        
        db.add_all([wb1, wb2])
        db.commit()
        
        # Search for "Python" in description
        response = client.get(
            "/api/v1/whiteboards/",
            headers=auth_headers,
            params={"search": "Python"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Board 1"
    
    def test_search_case_insensitive(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        """Test that search is case-insensitive."""
        # Create test whiteboard
        wb = Whiteboard(
            title="PYTHON PROGRAMMING",
            description="Learn Python basics",
            owner_id=test_user.id
        )
        
        db.add(wb)
        db.commit()
        
        # Search with different case
        response = client.get(
            "/api/v1/whiteboards/",
            headers=auth_headers,
            params={"search": "python"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "PYTHON PROGRAMMING"
    
    def test_search_partial_match(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        """Test that search performs partial matching."""
        # Create test whiteboards
        wb1 = Whiteboard(
            title="Programming Fundamentals",
            description="Basic programming concepts",
            owner_id=test_user.id
        )
        wb2 = Whiteboard(
            title="Advanced Programming",
            description="Advanced topics",
            owner_id=test_user.id
        )
        
        db.add_all([wb1, wb2])
        db.commit()
        
        # Search for partial match
        response = client.get(
            "/api/v1/whiteboards/",
            headers=auth_headers,
            params={"search": "gram"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Both contain "gram"
    
    def test_search_shared_whiteboards(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        """Test searching in shared whiteboards."""
        # Create another user
        other_user = User(
            email="other@example.com",
            name="Other User",
            password_hash="hashedpass"
        )
        db.add(other_user)
        db.commit()
        
        # Create whiteboard owned by other user
        wb = Whiteboard(
            title="Shared Python Board",
            description="Collaborative Python learning",
            owner_id=other_user.id
        )
        db.add(wb)
        db.commit()
        
        # Share with test user
        collab = WhiteboardCollaborator(
            whiteboard_id=wb.id,
            user_id=test_user.id,
            permission=Permission.VIEW
        )
        db.add(collab)
        db.commit()
        
        # Search should find shared whiteboard
        response = client.get(
            "/api/v1/whiteboards/",
            headers=auth_headers,
            params={"search": "Python"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Shared Python Board"
    
    def test_search_no_results(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        """Test search with no matching results."""
        # Create test whiteboard
        wb = Whiteboard(
            title="Mathematics Board",
            description="Math concepts and formulas",
            owner_id=test_user.id
        )
        
        db.add(wb)
        db.commit()
        
        # Search for non-existent term
        response = client.get(
            "/api/v1/whiteboards/",
            headers=auth_headers,
            params={"search": "Chemistry"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    def test_search_with_pagination(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        """Test search with pagination parameters."""
        # Create multiple whiteboards
        whiteboards = []
        for i in range(5):
            wb = Whiteboard(
                title=f"Python Board {i}",
                description=f"Board number {i}",
                owner_id=test_user.id
            )
            whiteboards.append(wb)
        
        db.add_all(whiteboards)
        db.commit()
        
        # Search with pagination
        response = client.get(
            "/api/v1/whiteboards/",
            headers=auth_headers,
            params={"search": "Python", "skip": 2, "limit": 2}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Limited to 2 results
    
    def test_search_empty_query(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        """Test that empty search query returns all whiteboards."""
        # Create test whiteboards
        wb1 = Whiteboard(
            title="Board 1",
            description="Description 1",
            owner_id=test_user.id
        )
        wb2 = Whiteboard(
            title="Board 2",
            description="Description 2",
            owner_id=test_user.id
        )
        
        db.add_all([wb1, wb2])
        db.commit()
        
        # Search with empty query
        response = client.get(
            "/api/v1/whiteboards/",
            headers=auth_headers,
            params={"search": ""}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Should return all whiteboards