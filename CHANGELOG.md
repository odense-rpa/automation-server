# Changelog

All notable changes to the Automation Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-07-25

### 🚀 Added

#### Core Features
- **Upcoming Executions**: New feature to view upcoming scheduled executions with API integration and UI component ([4f59257](https://github.com/odense-rpa/automation-server/commit/4f59257), [d83e9fd](https://github.com/odense-rpa/automation-server/commit/d83e9fd))
- **Work Duration Tracking**: Added work duration tracking fields to WorkItem model with comprehensive tests ([243f00a](https://github.com/odense-rpa/automation-server/commit/243f00a), [03a9d94](https://github.com/odense-rpa/automation-server/commit/03a9d94))
- **Session Parameters**: Optional parameters input for session creation in InstantSchedule component ([11ea9fb](https://github.com/odense-rpa/automation-server/commit/11ea9fb))
- **Trigger Logic Enhancement**: Implement trigger firing logic to prevent multiple activations within the same minute ([8c31b17](https://github.com/odense-rpa/automation-server/commit/8c31b17))
- **Work Item Reference API**: Endpoint to retrieve work items by reference with optional status filter ([27d2c6f](https://github.com/odense-rpa/automation-server/commit/27d2c6f), [33672fc](https://github.com/odense-rpa/automation-server/commit/33672fc))

#### Health & Monitoring
- **Health Check Endpoints**: Comprehensive health check implementation integrated into FastAPI application ([fa668fd](https://github.com/odense-rpa/automation-server/commit/fa668fd))
- **Enhanced Logging**: Refactored session logging to audit logging with new schema and enhanced functionality ([5ff9a35](https://github.com/odense-rpa/automation-server/commit/5ff9a35), [b9ce07e](https://github.com/odense-rpa/automation-server/commit/b9ce07e), [727e8e1](https://github.com/odense-rpa/automation-server/commit/727e8e1))

#### DevOps & Infrastructure
- **Docker Release Workflow**: Automated image building and pushing workflow ([6240b75](https://github.com/odense-rpa/automation-server/commit/6240b75))
- **Playwright Integration**: Docker and compose configuration updates for Playwright support ([7c0a63b](https://github.com/odense-rpa/automation-server/commit/7c0a63b))
- **Testing Infrastructure**: Docker dependency and PostgreSQL container fixture for testing ([4a42787](https://github.com/odense-rpa/automation-server/commit/4a42787))

### 🔧 Infrastructure & Docker Improvements

#### Build & Deployment
- **Multi-stage Dockerfile**: Refactored for worker and Playwright stages with improved build scripts ([52b4052](https://github.com/odense-rpa/automation-server/commit/52b4052), [fa668fd](https://github.com/odense-rpa/automation-server/commit/fa668fd))
- **Pre-built Images**: Updated docker-compose to use pre-built images and clean service definitions ([c9f0101](https://github.com/odense-rpa/automation-server/commit/c9f0101))
- **Environment Variables**: Better flexibility with API URL configuration using environment variables ([a5d014c](https://github.com/odense-rpa/automation-server/commit/a5d014c), [26f2ad7](https://github.com/odense-rpa/automation-server/commit/26f2ad7))

#### Performance & Security
- **Docker Optimization**: .dockerignore files to exclude unnecessary files from Docker context ([839e1eb](https://github.com/odense-rpa/automation-server/commit/839e1eb), [dbe37b3](https://github.com/odense-rpa/automation-server/commit/dbe37b3))
- **Nginx Configuration**: Performance optimizations and improved health checks ([dbe37b3](https://github.com/odense-rpa/automation-server/commit/dbe37b3))

### 🐛 Fixed

#### API & Backend
- **Token Order**: Removed sorting from fetchTokens method to maintain original token order ([9727d65](https://github.com/odense-rpa/automation-server/commit/9727d65))
- **Search Functionality**: Case-insensitive session log search and pagination improvements ([40b54f2](https://github.com/odense-rpa/automation-server/commit/40b54f2), [51cf9f3](https://github.com/odense-rpa/automation-server/commit/51cf9f3))
- **Database Queries**: Fixed scalar_one query result handling ([d06f88d](https://github.com/odense-rpa/automation-server/commit/d06f88d))
- **Pagination**: Improved counting in paginated workitem retrieval ([e9cc2c8](https://github.com/odense-rpa/automation-server/commit/e9cc2c8))

#### Frontend & UI
- **JSON Handling**: Enhanced JSON handling in Create and Edit Credential components ([9e007fe](https://github.com/odense-rpa/automation-server/commit/9e007fe))
- **Form Fields**: Updated form field values to use null instead of 0 for better empty state handling ([3e699ce](https://github.com/odense-rpa/automation-server/commit/3e699ce))
- **Credential Defaults**: Updated Credential data field default to empty dict ([37480f1](https://github.com/odense-rpa/automation-server/commit/37480f1))

#### Development & Configuration
- **Docker Entry Point**: Fixed entrypoint script for complete docker image ([fdc6534](https://github.com/odense-rpa/automation-server/commit/fdc6534))
- **Documentation URLs**: Fixed docs URL when run in docker ([0d40ab8](https://github.com/odense-rpa/automation-server/commit/0d40ab8))

### 🎨 UI/UX Improvements

#### Navigation & Interface
- **Active Route Highlighting**: Active routes now highlighted in navigation ([90354ee](https://github.com/odense-rpa/automation-server/commit/90354ee))
- **Button Improvements**: Streamlined Create/Edit buttons and added slots to DropdownButton ([84acc0a](https://github.com/odense-rpa/automation-server/commit/84acc0a))
- **Icon Updates**: Changed + to faPlay icon, fixed development console errors ([e204a8a](https://github.com/odense-rpa/automation-server/commit/e204a8a))
- **Loading Experience**: Fixed Workqueues loading experience and improved user feedback ([98d90d3](https://github.com/odense-rpa/automation-server/commit/98d90d3))

#### Data Presentation
- **Alphabetical Sorting**: Lists and tables now sorted alphabetically for better usability ([6d4a049](https://github.com/odense-rpa/automation-server/commit/6d4a049))
- **Row Interaction**: Editable rows no longer routable with cursor-pointer styling ([4877ab1](https://github.com/odense-rpa/automation-server/commit/4877ab1))
- **Delete Functionality**: Added delete workqueue functionality to the frontend ([4f25702](https://github.com/odense-rpa/automation-server/commit/4f25702))

### ⚙️ Refactoring & Architecture

#### Scheduler Architecture
- **Modular Scheduler**: Implemented modular scheduler architecture using Strategy pattern ([da6b972](https://github.com/odense-rpa/automation-server/commit/da6b972))
- **Trigger Processors**: Date and workqueue trigger processors with enhanced registry ([da6b972](https://github.com/odense-rpa/automation-server/commit/da6b972))
- **Parameter Validation**: Refactored parameter validation and trigger processing logic ([7df783e](https://github.com/odense-rpa/automation-server/commit/7df783e))
- **Graceful Shutdown**: Enhanced scheduler with parameter validation and graceful shutdown handling ([ac195f3](https://github.com/odense-rpa/automation-server/commit/ac195f3))
- **CronSim Migration**: Migrated to CronSim for improved cron handling ([ec7d362](https://github.com/odense-rpa/automation-server/commit/ec7d362))

#### Database & Models
- **Schema Improvements**: Refactored data types to use Dict instead of str in schemas and models ([8389641](https://github.com/odense-rpa/automation-server/commit/8389641))
- **Repository Enhancement**: Simplified get_next_workitem logic with skip_locked for better concurrency ([04bf0ef](https://github.com/odense-rpa/automation-server/commit/04bf0ef))
- **Database Configuration**: Updated database configurations and improved schema handling ([35af3af](https://github.com/odense-rpa/automation-server/commit/35af3af))

#### Code Quality
- **Code Structure**: Refactored code structure for improved readability and maintainability ([ab32981](https://github.com/odense-rpa/automation-server/commit/ab32981))
- **Clean Up**: Removed unused AccessTokenCreate schema and cleaned up repository comments ([e626f20](https://github.com/odense-rpa/automation-server/commit/e626f20))

### 📚 Documentation

- **Project Guidance**: Added CLAUDE.md for comprehensive project guidance and development instructions ([054e578](https://github.com/odense-rpa/automation-server/commit/054e578))
- **README Improvements**: Revised README.md for clarity and completeness with enhanced feature descriptions ([5c2d152](https://github.com/odense-rpa/automation-server/commit/5c2d152))
- **Installation Guide**: Updated installation guide with Docker setup and configuration ([b4ac33a](https://github.com/odense-rpa/automation-server/commit/b4ac33a))
- **Coding Conventions**: Added coding conventions and guidelines for Python and JavaScript ([b19a0ab](https://github.com/odense-rpa/automation-server/commit/b19a0ab))

### 🧪 Testing

- **Validation Tests**: Added validation tests for workitem update endpoint ([b31b20f](https://github.com/odense-rpa/automation-server/commit/b31b20f))
- **Pagination Tests**: Added pagination tests for workitems with and without search functionality ([9e427c4](https://github.com/odense-rpa/automation-server/commit/9e427c4))
- **Comprehensive Test Coverage**: Enhanced test coverage across scheduler, repositories, and API endpoints

### 🔄 Configuration & Environment

- **Environment Setup**: Included config example in backend and added .env to gitignore ([26bac80](https://github.com/odense-rpa/automation-server/commit/26bac80))
- **OpenAPI Configuration**: Added openapi_url to FastAPI configuration ([d6f260b](https://github.com/odense-rpa/automation-server/commit/d6f260b))
- **Version Bump**: Updated project version to 0.2.0 in pyproject.toml and uv.lock ([fa668fd](https://github.com/odense-rpa/automation-server/commit/fa668fd))

### 🔗 Dependencies & Libraries

- **CronSim Integration**: Migration to CronSim library for improved cron expression handling
- **Enhanced Testing**: Docker and PostgreSQL integration for comprehensive testing environment
- **Library Updates**: Various dependency updates and lock file maintenance

---

## [0.1.0] - 2025-05-19

### Initial Release
- Core automation server functionality
- Basic Docker compose setup for development
- Foundation for web-based automation management

---

**Note**: This changelog covers all changes from v0.1.0 to the current release/0.2.0 branch HEAD (commit a5b97f3). For detailed information about any specific change, please reference the commit hash provided with each entry.