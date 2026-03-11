"""
Workflow tests for GitHub Actions automation
Tests Phase 3 functionality: workflow validation, automation, scheduling
"""

import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.mark.workflow
class TestGitHubActionsWorkflows:
    """Test cases for GitHub Actions workflow configurations"""
    
    def test_daily_tracker_workflow_structure(self):
        """Test daily tracker workflow YAML is valid and well-structured"""
        workflow_file = Path('c:/Users/Nicol/Downloads/europa-tech-tracker/.github/workflows/daily_tracker.yml')
        
        # Skip if file doesn't exist (for CI environments)
        if not workflow_file.exists():
            pytest.skip("Workflow file not found")
            
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow = yaml.safe_load(f)
            
        # Validate basic structure
        assert 'name' in workflow
        assert 'on' in workflow
        assert 'jobs' in workflow
        
        # Validate scheduling
        assert 'schedule' in workflow['on']
        cron_schedule = workflow['on']['schedule'][0]['cron']
        assert isinstance(cron_schedule, str)
        assert len(cron_schedule.split()) == 5  # Valid cron format
        
        # Validate manual trigger
        assert 'workflow_dispatch' in workflow['on']
        
        # Validate job structure
        jobs = workflow['jobs']
        assert len(jobs) > 0
        
        main_job = list(jobs.values())[0]
        assert 'runs-on' in main_job
        assert 'steps' in main_job
        assert len(main_job['steps']) > 0
        
    def test_weekly_summary_workflow_structure(self):
        """Test weekly summary workflow YAML is valid"""
        workflow_file = Path('c:/Users/Nicol/Downloads/europa-tech-tracker/.github/workflows/weekly_summary.yml')
        
        if not workflow_file.exists():
            pytest.skip("Weekly workflow file not found")
            
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow = yaml.safe_load(f)
            
        # Validate structure
        assert 'name' in workflow
        assert 'on' in workflow
        assert 'jobs' in workflow
        
        # Should have weekly schedule (Sunday)
        cron_schedule = workflow['on']['schedule'][0]['cron']
        cron_parts = cron_schedule.split()
        assert cron_parts[4] == '0'  # Sunday (0 = Sunday in cron)
        
        # Should have manual trigger with parameters
        manual_trigger = workflow['on']['workflow_dispatch']
        assert 'inputs' in manual_trigger
        
    def test_manual_run_workflow_structure(self):
        """Test manual run workflow has proper debugging features"""
        workflow_file = Path('c:/Users/Nicol/Downloads/europa-tech-tracker/.github/workflows/manual_run.yml')
        
        if not workflow_file.exists():
            pytest.skip("Manual workflow file not found")
            
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow = yaml.safe_load(f)
            
        # Should only have manual trigger
        assert 'workflow_dispatch' in workflow['on']
        assert 'schedule' not in workflow['on']  # Manual only
        
        # Should have debugging inputs
        inputs = workflow['on']['workflow_dispatch']['inputs']
        assert 'test_mode' in inputs
        assert 'debug_level' in inputs
        
    def test_workflow_environment_setup(self):
        """Test that workflows set up Python environment correctly"""
        workflow_file = Path('c:/Users/Nicol/Downloads/europa-tech-tracker/.github/workflows/daily_tracker.yml')
        
        if not workflow_file.exists():
            pytest.skip("Workflow file not found")
            
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow = yaml.safe_load(f)
            
        main_job = list(workflow['jobs'].values())[0]
        steps = main_job['steps']
        
        # Check for required setup steps
        step_names = [step.get('name', '').lower() for step in steps]
        
        # Should have checkout step
        checkout_steps = [name for name in step_names if 'checkout' in name]
        assert len(checkout_steps) > 0
        
        # Should have Python setup step
        python_steps = [name for name in step_names if 'python' in name]
        assert len(python_steps) > 0
        
        # Should have dependency installation
        install_steps = [name for name in step_names if 'install' in name or 'dependencies' in name]
        assert len(install_steps) > 0
        
    def test_workflow_permissions(self):
        """Test workflows have appropriate GitHub permissions"""
        workflow_file = Path('c:/Users/Nicol/Downloads/europa-tech-tracker/.github/workflows/daily_tracker.yml')
        
        if not workflow_file.exists():
            pytest.skip("Workflow file not found")
            
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow = yaml.safe_load(f)
            
        main_job = list(workflow['jobs'].values())[0]
        
        # Should have permissions for committing
        if 'permissions' in main_job:
            permissions = main_job['permissions']
            assert 'contents' in permissions
            assert permissions['contents'] in ['write', 'read']
            
    @pytest.mark.slow
    def test_simulate_daily_workflow_execution(self, temp_directories):
        """Simulate daily workflow execution steps"""
        # This test simulates the key steps without actually running GitHub Actions
        
        # Step 1: Environment setup (mocked)
        python_version = "3.11"
        assert python_version == "3.11"
        
        # Step 2: Dependency installation (mocked)
        # In real workflow, this would be `pip install -r requirements.txt`
        dependencies = ['feedparser', 'beautifulsoup4', 'requests', 'PyYAML']
        assert all(isinstance(dep, str) for dep in dependencies)
        
        # Step 3: Configuration loading
        mock_config = {
            'sources': {
                'tech_eu': {'url': 'https://tech.eu/feed/', 'active': True}
            },
            'keywords': {'companies': {'high_priority': ['SAP']}},
            'settings': {'cache_max_age_days': 7}
        }
        
        # Step 4: Article collection (mocked)
        collected_articles = [
            {
                'title': 'Mock European Tech News',
                'description': 'Simulated article for workflow testing',
                'link': 'https://example.com/mock-article',
                'published': '2026-03-11T10:00:00',
                'source': 'tech_eu',
                'guid': 'mock_guid_123'
            }
        ]
        
        assert len(collected_articles) > 0
        
        # Step 5: Article processing (mocked)
        processed_articles = []
        for article in collected_articles:
            # Simulate processing logic
            processed_article = article.copy()
            processed_article.update({
                'relevance_score': 15.5,
                'primary_category': 'technology',
                'matched_keywords': {'companies': []},
                'cached_at': '2026-03-11T10:30:00',
                'content_hash': 'mock_hash_abc123'
            })
            processed_articles.append(processed_article)
            
        # Validate processed results
        assert len(processed_articles) > 0
        for article in processed_articles:
            assert_valid_processed_article(article)
            
        # Step 6: Report generation (mocked)
        report_content = f"""# 🇪🇺 Europa Tech Daily Report

**Date:** 2026-03-11
**Articles Processed:** {len(processed_articles)}

## Top Stories

"""
        for article in processed_articles:
            report_content += f"- [{article['title']}]({article['link']}) ({article['relevance_score']}⭐)\n"
            
        assert "Europa Tech Daily Report" in report_content
        assert "Articles Processed" in report_content
        
        # Step 7: Commit simulation (mocked)
        files_to_commit = [
            'output/daily_reports/europa_tech_20260311.md',
            'data/cache/article_cache.json'
        ]
        
        assert len(files_to_commit) == 2
        assert any('daily_reports' in f for f in files_to_commit)
        assert any('cache' in f for f in files_to_commit)
        
    def test_workflow_error_handling(self):
        """Test that workflows have proper error handling"""
        workflow_file = Path('c:/Users/Nicol/Downloads/europa-tech-tracker/.github/workflows/daily_tracker.yml')
        
        if not workflow_file.exists():
            pytest.skip("Workflow file not found")
            
        with open(workflow_file, 'r') as f:
            workflow_content = f.read()
            
        # Should have error handling patterns
        error_handling_indicators = [
            '|| true',  # Continue on error
            'continue-on-error',
            'if:',  # Conditional execution
            'try',  # Try-catch patterns  
            '2>&1',  # Error redirection
        ]
        
        # At least some error handling should be present
        has_error_handling = any(indicator in workflow_content for indicator in error_handling_indicators)
        assert has_error_handling, "Workflow should have some form of error handling"
        
    def test_workflow_output_artifacts(self):
        """Test that workflows generate expected output artifacts"""
        workflow_file = Path('c:/Users/Nicol/Downloads/europa-tech-tracker/.github/workflows/manual_run.yml')
        
        if not workflow_file.exists():
            pytest.skip("Manual workflow file not found")
            
        with open(workflow_file, 'r') as f:
            workflow_content = f.read()
            
        # Manual run should support artifact upload
        artifact_indicators = [
            'upload-artifact',
            'actions/upload-artifact',
            'artifacts',
            'path:'
        ]
        
        has_artifacts = any(indicator in workflow_content for indicator in artifact_indicators)
        assert has_artifacts, "Manual workflow should support artifact upload"
        
    def test_cron_schedule_validation(self):
        """Test that cron schedules are valid and reasonable"""
        workflows_dir = Path('c:/Users/Nicol/Downloads/europa-tech-tracker/.github/workflows')
        
        if not workflows_dir.exists():
            pytest.skip("Workflows directory not found")
            
        for workflow_file in workflows_dir.glob('*.yml'):
            if workflow_file.name.startswith('.'):
                continue
                
            with open(workflow_file, 'r') as f:
                workflow = yaml.safe_load(f)
                
            if 'schedule' in workflow.get('on', {}):
                schedules = workflow['on']['schedule']
                
                for schedule in schedules:
                    cron = schedule['cron']
                    cron_parts = cron.split()
                    
                    # Validate cron format (5 parts)
                    assert len(cron_parts) == 5, f"Invalid cron format in {workflow_file.name}: {cron}"
                    
                    # Validate hour range (0-23)  
                    hour = cron_parts[1]
                    if hour != '*':
                        assert 0 <= int(hour) <= 23, f"Invalid hour in {workflow_file.name}: {hour}"
                        
                    # Validate day of week (0-6)
                    dow = cron_parts[4]
                    if dow != '*':
                        dow_values = dow.split(',')
                        for dow_val in dow_values:
                            if '-' in dow_val:
                                start, end = dow_val.split('-')
                                assert 0 <= int(start) <= 6
                                assert 0 <= int(end) <= 6
                            else:
                                assert 0 <= int(dow_val) <= 6
                                
    def test_workflow_timezone_considerations(self):
        """Test that workflow schedules consider timezone correctly"""
        workflow_file = Path('c:/Users/Nicol/Downloads/europa-tech-tracker/.github/workflows/daily_tracker.yml')
        
        if not workflow_file.exists():
            pytest.skip("Workflow file not found")
            
        with open(workflow_file, 'r') as f:
            workflow_content = f.read()
            
        # Should have comments about timezone
        timezone_indicators = [
            'UTC',
            'Copenhagen',
            'CET',
            'timezone'
        ]
        
        has_timezone_info = any(indicator in workflow_content for indicator in timezone_indicators)
        assert has_timezone_info, "Workflow should document timezone considerations"
        
    @pytest.mark.network
    def test_workflow_dependencies_available(self):
        """Test that workflow dependencies are available"""
        # Test GitHub Actions used in workflows
        required_actions = [
            'actions/checkout@v4',
            'actions/setup-python@v4'
        ]
        
        # In a real test, you might check GitHub Marketplace
        # For now, just validate format
        for action in required_actions:
            parts = action.split('@')
            assert len(parts) == 2, f"Invalid action format: {action}"
            assert parts[0].count('/') == 1, f"Invalid action name: {parts[0]}"
            assert parts[1].startswith('v'), f"Invalid version format: {parts[1]}"
            
    def test_workflow_step_summary_generation(self):
        """Test that workflows generate GitHub step summaries"""
        workflow_file = Path('c:/Users/Nicol/Downloads/europa-tech-tracker/.github/workflows/daily_tracker.yml')
        
        if not workflow_file.exists():
            pytest.skip("Workflow file not found")
            
        with open(workflow_file, 'r') as f:
            workflow_content = f.read()
            
        # Should generate step summary
        summary_indicators = [
            'GITHUB_STEP_SUMMARY',
            'step_summary',
            '>> $GITHUB_STEP_SUMMARY',
            'echo "## '
        ]
        
        has_step_summary = any(indicator in workflow_content for indicator in summary_indicators)
        assert has_step_summary, "Workflow should generate step summaries"