"""
Documentation Agent - Generates comprehensive documentation for Flutter applications.
"""

import asyncio
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from shared.state import shared_state, AgentStatus, MessageType

class DocumentationAgent(BaseAgent):
    """
    The Documentation Agent specializes in creating comprehensive documentation.
    It generates technical docs, user guides, API documentation, and code comments.
    """
    
    def __init__(self):
        super().__init__("documentation")
        self.doc_types = [
            "technical_docs", "user_guides", "api_docs", "code_comments",
            "architecture_docs", "deployment_guides", "testing_docs"
        ]
        
    async def execute_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute documentation tasks."""
        if "generate_readme" in task_description:
            return await self._generate_readme(task_data)
        elif "create_api_docs" in task_description:
            return await self._create_api_documentation(task_data)
        elif "generate_user_guide" in task_description:
            return await self._generate_user_guide(task_data)
        elif "document_architecture" in task_description:
            return await self._document_architecture(task_data)
        else:
            return await self._handle_general_documentation_task(task_description, task_data)
    
    async def collaborate(self, collaboration_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle collaboration requests."""
        if collaboration_type == "documentation_review":
            return await self._review_documentation(data)
        elif collaboration_type == "generate_code_comments":
            return await self._generate_code_comments(data)
        elif collaboration_type == "create_release_notes":
            return await self._create_release_notes(data)
        else:
            return {"status": "unknown_collaboration_type", "type": collaboration_type}
    
    async def on_state_change(self, change_data: Dict[str, Any]) -> None:
        """React to state changes."""
        event = change_data.get("event")
        
        if event == "project_created":
            await self._create_initial_documentation(change_data["project_id"])
        elif event == "file_added":
            await self._update_documentation(change_data)
    
    async def _generate_readme(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive README.md for the project."""
        project_id = task_data["project_id"]
        
        project = shared_state.get_project_state(project_id)
        
        readme_prompt = f"""
        Generate a comprehensive README.md for this Flutter project:
        
        Project: {project.name}
        Description: {project.description}
        Requirements: {project.requirements}
        Architecture: {project.architecture_decisions}
        
        Create a professional README.md with these sections:
        
        # {project.name}
        
        ## 📱 Overview
        [Brief description of the app and its purpose]
        
        ## ✨ Features
        [List of key features]
        
        ## 🏗️ Architecture
        [Architecture overview with diagrams]
        
        ## 🚀 Getting Started
        
        ### Prerequisites
        - Flutter 3.16.0 or higher
        - Dart 3.0.0 or higher
        - Android Studio / VS Code
        - iOS development tools (for iOS builds)
        
        ### Installation
        ```bash
        # Clone the repository
        git clone https://github.com/username/{project.name.lower().replace(' ', '_')}.git
        
        # Navigate to project directory
        cd {project.name.lower().replace(' ', '_')}
        
        # Install dependencies
        flutter pub get
        
        # Run code generation (if needed)
        flutter packages pub run build_runner build
        
        # Run the app
        flutter run
        ```
        
        ### Configuration
        [Environment setup, API keys, etc.]
        
        ## 📱 Platforms
        - ✅ Android
        - ✅ iOS
        - ✅ Web
        - ✅ Desktop (Windows, macOS, Linux)
        
        ## 🧪 Testing
        ```bash
        # Run unit tests
        flutter test
        
        # Run integration tests
        flutter test integration_test/
        
        # Generate coverage report
        flutter test --coverage
        genhtml coverage/lcov.info -o coverage/html
        ```
        
        ## 📦 Building
        
        ### Android
        ```bash
        # Debug APK
        flutter build apk --debug
        
        # Release APK
        flutter build apk --release
        
        # App Bundle (recommended for Play Store)
        flutter build appbundle --release
        ```
        
        ### iOS
        ```bash
        # Debug build
        flutter build ios --debug --no-codesign
        
        # Release build
        flutter build ios --release
        
        # IPA for distribution
        flutter build ipa --release
        ```
        
        ## 🏛️ Architecture
        
        ### State Management
        [Chosen state management solution and reasoning]
        
        ### Project Structure
        ```
        lib/
        ├── core/
        │   ├── constants/
        │   ├── errors/
        │   ├── utils/
        │   └── themes/
        ├── features/
        │   └── [feature_name]/
        │       ├── data/
        │       ├── domain/
        │       └── presentation/
        ├── shared/
        │   ├── widgets/
        │   └── utils/
        └── main.dart
        ```
        
        ### Dependencies
        [Key dependencies and their purposes]
        
        ## 🔒 Security
        [Security features and considerations]
        
        ## 🚀 Deployment
        [Deployment process and CI/CD]
        
        ## 📊 Performance
        [Performance considerations and optimizations]
        
        ## 🤝 Contributing
        1. Fork the repository
        2. Create a feature branch
        3. Make your changes
        4. Add tests for new functionality
        5. Run tests and ensure they pass
        6. Submit a pull request
        
        ## 📄 License
        This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
        
        ## 🙏 Acknowledgments
        [Credits and acknowledgments]
        
        ## 📞 Support
        [Contact information and support channels]
        
        Include badges for build status, coverage, version, etc.
        Make it visually appealing with emojis and proper formatting.
        """
        
        readme_content = await self.think(readme_prompt, {
            "project": project,
            "doc_types": self.doc_types
        })
        
        # Store in project documentation
        if project:
            project.documentation["README.md"] = readme_content
            shared_state.update_project(project_id, documentation=project.documentation)
        
        return {
            "document_type": "README",
            "content": readme_content,
            "status": "generated"
        }
    
    async def _create_api_documentation(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive API documentation."""
        project_id = task_data["project_id"]
        api_endpoints = task_data.get("endpoints", [])
        
        api_docs_prompt = f"""
        Create comprehensive API documentation for these endpoints:
        {api_endpoints}
        
        Generate API documentation including:
        
        # API Documentation
        
        ## Base URL
        ```
        Production: https://api.example.com/v1
        Staging: https://api-staging.example.com/v1
        Development: https://api-dev.example.com/v1
        ```
        
        ## Authentication
        All API requests require authentication using Bearer tokens:
        ```
        Authorization: Bearer <your_access_token>
        ```
        
        ## Rate Limiting
        - 1000 requests per hour per user
        - 100 requests per minute per IP
        
        ## Error Responses
        The API uses conventional HTTP response codes:
        
        | Code | Meaning |
        |------|---------|
        | 200 | OK - Everything worked as expected |
        | 400 | Bad Request - Invalid request parameters |
        | 401 | Unauthorized - Invalid API key |
        | 403 | Forbidden - Insufficient permissions |
        | 404 | Not Found - Resource doesn't exist |
        | 500 | Internal Server Error - Something went wrong |
        
        Error Response Format:
        ```json
        {
          "error": {
            "code": "INVALID_REQUEST",
            "message": "The request is invalid",
            "details": "Email address is required"
          }
        }
        ```
        
        ## Endpoints
        
        ### Authentication
        
        #### POST /auth/login
        Authenticate user and get access token.
        
        **Request:**
        ```json
        {
          "email": "user@example.com",
          "password": "password123"
        }
        ```
        
        **Response:**
        ```json
        {
          "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
          "refresh_token": "dGhpc2lzYXJlZnJlc2h0b2tlbg...",
          "expires_in": 3600,
          "user": {
            "id": "123",
            "email": "user@example.com",
            "name": "John Doe"
          }
        }
        ```
        
        ### Users
        
        #### GET /users/me
        Get current user profile.
        
        **Headers:**
        ```
        Authorization: Bearer <access_token>
        ```
        
        **Response:**
        ```json
        {
          "id": "123",
          "email": "user@example.com",
          "name": "John Doe",
          "avatar": "https://example.com/avatar.jpg",
          "created_at": "2023-01-01T00:00:00Z",
          "updated_at": "2023-01-01T00:00:00Z"
        }
        ```
        
        #### PUT /users/me
        Update current user profile.
        
        **Request:**
        ```json
        {
          "name": "Jane Doe",
          "avatar": "https://example.com/new-avatar.jpg"
        }
        ```
        
        **Response:**
        ```json
        {
          "id": "123",
          "email": "user@example.com",
          "name": "Jane Doe",
          "avatar": "https://example.com/new-avatar.jpg",
          "updated_at": "2023-01-02T00:00:00Z"
        }
        ```
        
        ## SDKs and Libraries
        
        ### Flutter SDK
        DART_CODE_REMOVED
        
        ## Webhooks
        [Webhook documentation if applicable]
        
        ## Changelog
        [API version changes and updates]
        
        Include comprehensive examples, request/response schemas, and error handling.
        """
        
        api_documentation = await self.think(api_docs_prompt, {
            "endpoints": api_endpoints,
            "project": shared_state.get_project_state(project_id)
        })
        
        return {
            "document_type": "API",
            "endpoints": api_endpoints,
            "documentation": api_documentation,
            "status": "generated"
        }
    
    async def _generate_user_guide(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate user guide and tutorials."""
        project_id = task_data["project_id"]
        features = task_data.get("features", [])
        
        user_guide_prompt = f"""
        Create a comprehensive user guide for this Flutter app:
        
        Features: {features}
        
        Generate user documentation including:
        
        # User Guide
        
        ## Getting Started
        
        ### Download and Installation
        1. **Android Users:**
           - Visit Google Play Store
           - Search for "[App Name]"
           - Tap "Install"
           - Open the app
        
        2. **iOS Users:**
           - Visit App Store
           - Search for "[App Name]"
           - Tap "Get"
           - Open the app
        
        ### First Launch
        1. Open the app
        2. Complete the onboarding tutorial
        3. Create your account or sign in
        4. Grant necessary permissions
        5. Start using the app!
        
        ## Account Management
        
        ### Creating an Account
        1. Tap "Sign Up" on the welcome screen
        2. Enter your email address
        3. Create a secure password
        4. Verify your email address
        5. Complete your profile
        
        ### Signing In
        1. Open the app
        2. Tap "Sign In"
        3. Enter your email and password
        4. Tap "Sign In"
        
        ### Password Reset
        1. On the sign-in screen, tap "Forgot Password?"
        2. Enter your email address
        3. Check your email for reset instructions
        4. Follow the link to create a new password
        
        ## Core Features
        
        [For each feature, provide:]
        
        ### [Feature Name]
        **What it does:** [Brief description]
        
        **How to use it:**
        1. Step-by-step instructions
        2. With screenshots
        3. Common use cases
        4. Tips and tricks
        
        **Troubleshooting:**
        - Common issues and solutions
        - Error messages and what they mean
        - When to contact support
        
        ## Settings and Customization
        
        ### Accessing Settings
        1. Tap the menu icon (☰) in the top-left corner
        2. Select "Settings"
        
        ### Available Settings
        - **Profile Settings:** Update your name, email, and avatar
        - **Privacy Settings:** Control data sharing and visibility
        - **Notification Settings:** Manage push notifications
        - **Theme Settings:** Choose light or dark mode
        - **Language Settings:** Select your preferred language
        
        ## Privacy and Security
        
        ### Data Protection
        - Your data is encrypted and secure
        - We never share personal information
        - You can delete your account at any time
        
        ### Account Security
        - Use a strong, unique password
        - Enable biometric authentication
        - Keep the app updated
        - Log out from shared devices
        
        ## Troubleshooting
        
        ### Common Issues
        
        **App Won't Start**
        - Check your internet connection
        - Restart the app
        - Update to the latest version
        - Restart your device
        
        **Login Problems**
        - Verify your email and password
        - Check for typos
        - Reset your password if needed
        - Clear app cache (Android)
        
        **Performance Issues**
        - Close other apps
        - Free up device storage
        - Check internet speed
        - Update the app
        
        ### Getting Help
        
        **In-App Support**
        1. Go to Settings → Help & Support
        2. Browse FAQ or contact support
        3. Describe your issue in detail
        4. Include screenshots if helpful
        
        **Contact Information**
        - Email: support@example.com
        - Website: https://example.com/support
        - Phone: 1-800-SUPPORT
        
        ## Frequently Asked Questions
        
        **Q: Is the app free to use?**
        A: [Answer about pricing and features]
        
        **Q: Can I use the app offline?**
        A: [Answer about offline capabilities]
        
        **Q: How do I delete my account?**
        A: [Step-by-step deletion process]
        
        ## Tips and Best Practices
        
        ### Getting the Most Out of the App
        - [Productivity tips]
        - [Hidden features]
        - [Workflow recommendations]
        - [Integration with other apps]
        
        ### Performance Tips
        - Keep the app updated
        - Regularly clear cache
        - Manage storage space
        - Use Wi-Fi when possible
        
        Include screenshots, GIFs, and videos where helpful.
        Make instructions clear and easy to follow.
        """
        
        user_guide = await self.think(user_guide_prompt, {
            "features": features,
            "project": shared_state.get_project_state(project_id)
        })
        
        return {
            "document_type": "user_guide",
            "features": features,
            "guide": user_guide,
            "status": "generated"
        }
    
    async def _document_architecture(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Document the application architecture."""
        project_id = task_data["project_id"]
        
        project = shared_state.get_project_state(project_id)
        
        architecture_docs_prompt = f"""
        Create comprehensive architecture documentation:
        
        Project: {project.name}
        Architecture Decisions: {project.architecture_decisions}
        
        Generate technical architecture documentation:
        
        # Architecture Documentation
        
        ## System Overview
        [High-level system description with diagrams]
        
        ## Architecture Principles
        - **Separation of Concerns:** Clear boundaries between layers
        - **Dependency Inversion:** Abstractions don't depend on details
           # - **Single Responsibility:** Each class has one reason to change
        - **Open/Closed Principle:** Open for extension, closed for modification
        
        ## Layer Architecture
        
        ### Presentation Layer
        - **Responsibility:** UI rendering and user interaction
           # - **Components:** Widgets, Screens, State Management
        - **Dependencies:** Domain layer only
        
        ### Domain Layer
        - **Responsibility:** Business logic and rules
        - **Components:** Entities, Use Cases, Repository Interfaces
        - **Dependencies:** None (pure Dart)
        
        ### Data Layer
        - **Responsibility:** Data access and external services
        - **Components:** Repository Implementations, Data Sources, Models
        - **Dependencies:** Domain layer
        
        ## State Management
        [Detailed explanation of chosen state management solution]
        
        ## Dependency Injection
        [DI container setup and service registration]
        
        ## Navigation
        [Routing strategy and navigation flow]
        
        ## Data Flow
        [How data flows through the application layers]
        
        ## Error Handling
        [Global error handling strategy]
        
        ## Testing Strategy
        [Unit, widget, and integration test approach]
        
        ## Security Architecture
        [Security measures and data protection]
        
        ## Performance Considerations
        [Optimization strategies and monitoring]
        
        ## Deployment Architecture
        [Build and deployment pipeline]
        
        ## Decision Records
        [Important architectural decisions and rationale]
        
        Include diagrams, code examples, and rationale for decisions.
        """
        
        architecture_documentation = await self.think(architecture_docs_prompt, {
            "project": project,
            "doc_types": self.doc_types
        })
        
        return {
            "document_type": "architecture",
            "documentation": architecture_documentation,
            "status": "generated"
        }
    
    async def _generate_code_comments(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive code comments."""
        code = data.get("code", "")
        file_type = data.get("file_type", "dart")
        
        comments_prompt = f"""
        Add comprehensive code comments to this {file_type} code:
        
        {code}
        
        Add:
        1. Class-level documentation
        2. Method documentation with parameters and return values
        3. Complex logic explanations
        4. TODO comments for future improvements
        5. Warning comments for important considerations
        
        Follow Dart documentation conventions:
        DART_CODE_REMOVED
        
        Make comments helpful and informative.
        """
        
        commented_code = await self.think(comments_prompt, {
            "code": code,
            "file_type": file_type
        })
        
        return {
            "original_code": code,
            "commented_code": commented_code,
            "file_type": file_type
        }
    
    async def _create_initial_documentation(self, project_id: str) -> None:
        """Create initial documentation for a new project."""
        await self._generate_readme({"project_id": project_id})
    
    async def _handle_general_documentation_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general documentation tasks."""
        response = await self.think(f"Handle documentation task: {task_description}", task_data)
        return {"response": response, "task": task_description}
