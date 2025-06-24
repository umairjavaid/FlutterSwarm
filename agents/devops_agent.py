"""
DevOps Agent - Manages deployment and CI/CD pipelines for Flutter applications.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from shared.state import shared_state, AgentStatus, MessageType
from utils.function_logger import track_function

class DevOpsAgent(BaseAgent):
    """
    The DevOps Agent specializes in deployment and CI/CD pipeline management.
    It handles build automation, testing pipelines, and deployment strategies.
    """
    
    def __init__(self):
        super().__init__("devops")
        self.platforms = ["android", "ios", "web", "desktop"]
        self.ci_systems = ["github_actions", "gitlab_ci", "azure_pipelines", "bitbucket"]
        self.deployment_targets = ["app_store", "play_store", "firebase_hosting", "web_hosting"]
        
    @track_function(log_args=True, log_return=True)
    async def execute_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute DevOps tasks."""
        try:
            # Analyze task using LLM to understand DevOps requirements
            analysis = await self.think(f"Analyze this DevOps task: {task_description}", {
                "task_data": task_data,
                "platforms": self.platforms,
                "ci_systems": self.ci_systems,
                "deployment_targets": self.deployment_targets
            })
            
            self.logger.info(f"🚀 DevOps Agent executing task: {task_description}")
            
            # Execute appropriate task with retry mechanism
            result = None
            if "setup_ci_cd" in task_description:
                result = await self.safe_execute_with_retry(
                    lambda: self._setup_ci_cd_pipeline(task_data)
                )
            elif "configure_deployment" in task_description:
                result = await self.safe_execute_with_retry(
                    lambda: self._configure_deployment(task_data)
                )
            elif "setup_monitoring" in task_description:
                result = await self.safe_execute_with_retry(
                    lambda: self._setup_monitoring(task_data)
                )
            elif "create_build_scripts" in task_description:
                result = await self.safe_execute_with_retry(
                    lambda: self._create_build_scripts(task_data)
                )
            else:
                result = await self.safe_execute_with_retry(
                    lambda: self._handle_general_devops_task(task_description, task_data)
                )
            
            # Add execution metadata
            result.update({
                "task_type": task_description,
                "execution_time": datetime.now().isoformat(),
                "agent": self.agent_id,
                "platforms_considered": self.platforms,
                "task_analysis": analysis[:200] + "..." if len(analysis) > 200 else analysis
            })
            
            return result
            
        except Exception as e:
            import traceback
            self.logger.error(f"❌ Error executing DevOps task: {str(e)}\n{traceback.format_exc()}")
            return {
                "status": "failed",
                "error": str(e),
                "task_type": task_description,
                "execution_time": datetime.now().isoformat(),
                "agent": self.agent_id
            }
    
    async def collaborate(self, collaboration_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle collaboration requests."""
        if collaboration_type == "architecture_review":
            return await self._review_deployment_architecture(data)
        elif collaboration_type == "build_optimization":
            return await self._optimize_build_process(data)
        elif collaboration_type == "deployment_strategy":
            return await self._recommend_deployment_strategy(data)
        else:
            return {"status": "unknown_collaboration_type", "type": collaboration_type}
    
    async def on_state_change(self, change_data: Dict[str, Any]) -> None:
        """React to state changes."""
        event = change_data.get("event")
        
        if event == "implementation_completed":
            await self._prepare_deployment(change_data["project_id"])
        elif event == "testing_completed":
            await self._setup_automated_deployment(change_data["project_id"])
    
    async def _setup_ci_cd_pipeline(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Set up CI/CD pipeline for the Flutter project."""
        project_id = task_data["project_id"]
        platforms = task_data.get("platforms", ["android", "ios"])
        ci_system = task_data.get("ci_system", "github_actions")
        
        project = shared_state.get_project_state(project_id)
        
        # Get CI/CD configuration from config
        config = self.config_manager
        cicd_config = config.get_deployment_config().get('cicd', {})
        flutter_version = cicd_config.get('flutter_version', '3.16.0')
        java_version = cicd_config.get('java_version', '11')
        java_distribution = cicd_config.get('java_distribution', 'zulu')
        checkout_version = cicd_config.get('checkout_version', 'v3')
        flutter_action_version = cicd_config.get('flutter_action_version', 'v2')
        java_setup_version = cicd_config.get('java_setup_version', 'v3')
        codecov_version = cicd_config.get('codecov_version', 'v3')
        
        # Defensively access project attributes
        project_name = getattr(project, 'name', 'Unknown Project')
        
        cicd_prompt = f"""
        Create a comprehensive CI/CD pipeline for this Flutter project:
        
        Project: {project_name}
        Platforms: {platforms}
        CI System: {ci_system}
        
        Generate complete CI/CD configuration including:
        
        1. **GitHub Actions Workflow** (if github_actions):
           ```yaml
           name: Flutter CI/CD
           
           on:
             push:
               branches: [main, develop]
             pull_request:
               branches: [main]
           
           jobs:
             test:
               runs-on: ubuntu-latest
               steps:
                 - uses: actions/checkout@{checkout_version}
                 - uses: subosito/flutter-action@{flutter_action_version}
                   with:
                     flutter-version: '{flutter_version}'
                 - run: flutter pub get
                 - run: flutter analyze
                 - run: command_flutter test --coverage
                   # The above command is a placeholder for the Flutter test command
                 - uses: codecov/codecov-action@{codecov_version}
           
             build-android:
               needs: test
               runs-on: ubuntu-latest
               if: github.ref == 'refs/heads/main'
               steps:
                 - uses: actions/checkout@{checkout_version}
                 - uses: subosito/flutter-action@{flutter_action_version}
                 - uses: actions/setup-java@{java_setup_version}
                   with:
                     distribution: '{java_distribution}'
                     java-version: '{java_version}'
                 - run: command_flutter build apk --release
                   # The above command is a placeholder for the Flutter build command
                 - run: command_flutter build appbundle --release
                   # The above command is a placeholder for the Flutter build command
           
             build-ios:
               needs: test
               runs-on: macos-latest
               if: github.ref == 'refs/heads/main'
               steps:
                 - uses: actions/checkout@{checkout_version}
                 - uses: subosito/flutter-action@{flutter_action_version}
                 - run: command_flutter build ios --release --no-codesign
                   # The above command is a placeholder for the Flutter build command
           ```
        
        2. **Build Configuration**:
           - Environment-specific builds
           - Code signing setup
           - Asset optimization
           - Obfuscation settings
        
        3. **Testing Pipeline**:
           - Unit test execution
           # - Widget test execution
           - Integration test execution
           - Code coverage reporting
           - Test result publishing
        
        4. **Quality Gates**:
           - Code quality checks
           - Security scanning
           - Performance testing
           - Dependency vulnerability scanning
        
        5. **Artifact Management**:
           - Build artifact storage
           - Version tagging
           - Release notes generation
           - Changelog automation
        
        6. **Deployment Automation**:
           - Staging deployment
           - Production deployment
           - Rollback strategies
           - Blue-green deployment
        
        7. **Notification System**:
           - Build status notifications
           - Deployment notifications
           - Failure alerts
           - Success confirmations
        
        Include specific configurations for each target platform and deployment strategy.
        """
        
        cicd_config = await self.think(cicd_prompt, {
            "project": project,
            "platforms": platforms,
            "ci_system": ci_system,
            "ci_systems": self.ci_systems
        })
        
        # Store deployment configuration
        deployment_config = {
            "ci_system": ci_system,
            "platforms": platforms,
            "pipeline_config": cicd_config,
            "status": "configured"
        }
        
        shared_state.update_project(project_id, deployment_config=deployment_config)
        
        return {
            "ci_system": ci_system,
            "platforms": platforms,
            "configuration": cicd_config,
            "status": "configured"
        }
    
    async def _configure_deployment(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Configure deployment settings for different environments."""
        project_id = task_data["project_id"]
        environments = task_data.get("environments", ["staging", "production"])
        
        deployment_prompt = f"""
        Configure deployment settings for these environments: {environments}
        
        Create deployment configuration including:
        
        1. **Environment Configuration**:
           DART_CODE_REMOVED
        
        2. **Build Flavors**:
           - Android build.gradle configuration
           - iOS scheme configuration
           - Environment-specific assets
           - Feature flags
        
        3. **Deployment Scripts**:
           ```bash
           #!/bin/bash
           # deploy.sh
           
           ENV=$1
           PLATFORM=$2
           
           case $ENV in
             staging)
               echo "Deploying to staging..."
               command_flutter build $PLATFORM --flavor staging
               # The above command is a placeholder for the Flutter build command
               ;;
             production)
               echo "Deploying to production..."
               command_flutter build $PLATFORM --flavor production --obfuscate
               # The above command is a placeholder for the Flutter build command
               ;;
           esac
           ```
        
        4. **App Store Configuration**:
           - App Store Connect setup
           - Fastlane configuration
           - Metadata management
           - Screenshot automation
        
        5. **Play Store Configuration**:
           - Google Play Console setup
           - Supply configuration
           - Internal testing tracks
           - Staged rollouts
        
        6. **Web Deployment**:
           - Firebase Hosting
           - CDN configuration
           - Custom domain setup
           - SSL certificate management
        
        7. **Monitoring Setup**:
           - Crashlytics integration
           - Analytics configuration
           - Performance monitoring
           - Error tracking
        
        Provide complete deployment configuration for all target platforms.
        """
        
        deployment_config = await self.think(deployment_prompt, {
            "environments": environments,
            "platforms": self.platforms,
            "deployment_targets": self.deployment_targets
        })
        
        return {
            "environments": environments,
            "configuration": deployment_config,
            "status": "configured"
        }
    
    async def _setup_monitoring(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Set up monitoring and observability."""
        project_id = task_data["project_id"]
        monitoring_types = task_data.get("types", ["crash_reporting", "analytics", "performance"])
        
        monitoring_prompt = f"""
        Set up comprehensive monitoring for these types: {monitoring_types}
        
        Implement monitoring configuration:
        
        1. **Crash Reporting** (Firebase Crashlytics):
           DART_CODE_REMOVED
        
        2. **Analytics Integration**:
           DART_CODE_REMOVED
        
        3. **Performance Monitoring**:
           DART_CODE_REMOVED
        
        4. **Health Checks**:
           - App startup monitoring
           - API response time tracking
           - Memory usage monitoring
           - Battery usage tracking
        
        5. **Custom Metrics**:
           - Business KPI tracking
           - User engagement metrics
           - Feature usage analytics
           - Conversion funnel tracking
        
        6. **Alerting System**:
           - Crash rate alerts
           - Performance degradation alerts
           - Error rate thresholds
           - Custom metric alerts
        
        7. **Dashboard Configuration**:
           - Firebase console setup
           - Custom dashboard creation
           - Metric visualization
           - Report automation
        
        Provide complete monitoring implementation with proper initialization and usage.
        """
        
        monitoring_config = await self.think(monitoring_prompt, {
            "monitoring_types": monitoring_types,
            "project": shared_state.get_project_state(project_id)
        })
        
        return {
            "monitoring_types": monitoring_types,
            "configuration": monitoring_config,
            "status": "configured"
        }
    
    async def _create_build_scripts(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create build automation scripts."""
        project_id = task_data["project_id"]
        platforms = task_data.get("platforms", ["android", "ios"])
        
        # Get build configuration from config
        config = self.config_manager
        build_config = config.get_deployment_config().get('build', {})
        clean_before_build = build_config.get('clean_before_build', True)
        run_code_generation = build_config.get('run_code_generation', True)
        obfuscate_release = build_config.get('obfuscate_release', True)
        split_debug_info = build_config.get('split_debug_info', 'symbols/')
        
        build_scripts_prompt = f"""
        Create comprehensive build scripts for platforms: {platforms}
        
        Generate build automation scripts:
        
        1. **Master Build Script** (build.sh):
           ```bash
           #!/bin/bash
           
           set -e
           
           PLATFORM=$1
           FLAVOR=$2
           BUILD_TYPE=$3
           
           echo "Building Flutter app for $PLATFORM ($FLAVOR - $BUILD_TYPE)"
           
           # Clean previous builds
           {"flutter clean" if clean_before_build else "# Skipping clean"}
           flutter pub get
           
           # Run code generation
           {"flutter packages pub run build_runner build --delete-conflicting-outputs" if run_code_generation else "# Skipping code generation"}
           
           # Run tests
           command_flutter test
           # The above command is a placeholder for the Flutter test command
           
           # Build for platform
           case $PLATFORM in
             android)
               if [ "$BUILD_TYPE" = "release" ]; then
                 command_flutter build appbundle --flavor $FLAVOR {"--obfuscate --split-debug-info=" + split_debug_info if obfuscate_release else ""}
                 # The above command is a placeholder for the Flutter build command
               else
                 command_flutter build apk --flavor $FLAVOR
                 # The above command is a placeholder for the Flutter build command
               fi
               ;;
             ios)
               if [ "$BUILD_TYPE" = "release" ]; then
                 command_flutter build ipa --flavor $FLAVOR {"--obfuscate --split-debug-info=" + split_debug_info if obfuscate_release else ""}
                 # The above command is a placeholder for the Flutter build command
               else
                 command_flutter build ios --flavor $FLAVOR --no-codesign
                 # The above command is a placeholder for the Flutter build command
               fi
               ;;
             web)
               command_flutter build web --flavor $FLAVOR
               # The above command is a placeholder for the Flutter build command
               ;;
           esac
           ```
        
        2. **Platform-specific Scripts**:
        Provide complete build automation setup with proper error handling and logging.
        """
        
        build_scripts = await self.think(build_scripts_prompt, {
            "platforms": platforms,
            "project": shared_state.get_project_state(project_id)
        })
        
        return {
            "platforms": platforms,
            "scripts": build_scripts,
            "status": "created"
        }
    
    async def _review_deployment_architecture(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Review architecture for deployment considerations."""
        architecture = data.get("architecture", "")
        focus = data.get("focus", "deployment_considerations")
        
        review_prompt = f"""
        Review this architecture from a deployment perspective:
        
        Architecture: {architecture}
        Focus: {focus}
        
        Analyze:
        1. Deployment complexity
        2. Scalability considerations
        3. Platform-specific challenges
        4. CI/CD pipeline requirements
        5. Monitoring and observability needs
        6. Rollback strategies
        
        Provide specific deployment recommendations.
        """
        
        deployment_review = await self.think(review_prompt, {
            "architecture": architecture,
            "platforms": self.platforms,
            "deployment_targets": self.deployment_targets
        })
        
        return {
            "deployment_review": deployment_review,
            "focus": focus,
            "reviewer": self.agent_id
        }
    
    async def _handle_general_devops_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general DevOps tasks."""
        response = await self.think(f"Handle DevOps task: {task_description}", task_data)
        return {"response": response, "task": task_description}
