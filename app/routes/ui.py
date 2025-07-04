from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import logging


logger = logging.getLogger(__name__)
router = APIRouter()


# HTML точка входа - простой статический HTML вместо FastUI
@router.get("/ui/{path:path}")
async def html_landing() -> HTMLResponse:
    """Простой статический веб-интерфейс"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reqres API Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 3rem 0; }
            .card { border: none; box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15); }
            .stat-card { background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%); color: white; }
        </style>
    </head>
    <body>
        <div class="hero">
            <div class="container">
                <h1 class="display-4">🚀 Reqres API Dashboard</h1>
                <p class="lead">FastAPI + PostgreSQL + Bootstrap</p>
            </div>
        </div>

        <div class="container mt-5">
            <!-- System Status -->
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="card stat-card text-center p-4">
                        <h3 id="db-status">🗄️ Database</h3>
                        <p class="mb-0">Connected</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card stat-card text-center p-4">
                        <h3 id="users-count">👥 Users</h3>
                        <p class="mb-0" id="users-number">Loading...</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card stat-card text-center p-4">
                        <h3 id="resources-count">🎨 Resources</h3>
                        <p class="mb-0" id="resources-number">Loading...</p>
                    </div>
                </div>
            </div>

            <!-- CRUD Operations -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h4>🧭 CRUD Operations</h4>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h5>👥 Users Management</h5>
                                    <div class="btn-group-vertical w-100 mb-3">
                                        <button class="btn btn-primary" onclick="loadUsers()">📋 View All Users</button>
                                        <button class="btn btn-success" onclick="showCreateUser()">➕ Create User</button>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <h5>🎨 Resources Management</h5>
                                    <div class="btn-group-vertical w-100 mb-3">
                                        <button class="btn btn-info" onclick="loadResources()">🌈 View All Resources</button>
                                        <button class="btn btn-warning" onclick="showCreateResource()">🎯 Create Resource</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Data Display Area -->
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h4 id="data-title">📊 Data View</h4>
                        </div>
                        <div class="card-body">
                            <div id="data-content">
                                <p class="text-muted">Select an operation above to view data</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quick Links -->
            <div class="row mt-4 mb-5">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h4>🔗 Documentation & Tools</h4>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-3">
                                    <a href="/docs" class="btn btn-outline-primary w-100 mb-2">📖 API Documentation</a>
                                </div>
                                <div class="col-md-3">
                                    <a href="http://localhost:8080" target="_blank" class="btn btn-outline-secondary w-100 mb-2">🛠️ Database Admin</a>
                                </div>
                                <div class="col-md-3">
                                    <a href="/status" class="btn btn-outline-success w-100 mb-2">❤️ Health Check</a>
                                </div>
                                <div class="col-md-3">
                                    <button class="btn btn-outline-info w-100 mb-2" onclick="runTests()">🧪 Test API</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Load stats on page load
            document.addEventListener('DOMContentLoaded', function() {
                loadStats();
            });

            async function loadStats() {
                try {
                    const usersResponse = await fetch('/api/users?size=1');
                    const usersData = await usersResponse.json();
                    document.getElementById('users-number').textContent = usersData.total || 0;

                    const resourcesResponse = await fetch('/api/resources?size=1');
                    const resourcesData = await resourcesResponse.json();
                    document.getElementById('resources-number').textContent = resourcesData.total || 0;
                } catch (error) {
                    console.error('Error loading stats:', error);
                }
            }

            async function loadUsers() {
                document.getElementById('data-title').textContent = '👥 Users Management';
                try {
                    const response = await fetch('/api/users?size=50');
                    const data = await response.json();
                    let html = '<div class="table-responsive"><table class="table table-striped"><thead>';
                    html += '<tr><th>ID</th><th>First Name</th><th>Last Name</th><th>Email</th><th>Actions</th></tr></thead><tbody>';

                    data.items.forEach(user => {
                        html += `<tr>
                            <td>${user.id}</td>
                            <td>${user.first_name}</td>
                            <td>${user.last_name}</td>
                            <td>${user.email}</td>
                            <td>
                                <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.id})">🗑️ Delete</button>
                            </td>
                        </tr>`;
                    });
                    html += '</tbody></table></div>';
                    document.getElementById('data-content').innerHTML = html;
                } catch (error) {
                    document.getElementById('data-content').innerHTML = '<div class="alert alert-danger">Error loading users</div>';
                }
            }

            async function loadResources() {
                document.getElementById('data-title').textContent = '🎨 Resources Gallery';
                try {
                    const response = await fetch('/api/resources?size=50');
                    const data = await response.json();
                    let html = '<div class="table-responsive"><table class="table table-striped"><thead>';
                    html += '<tr><th>ID</th><th>Color Name</th><th>Year</th><th>Hex Code</th><th>Pantone</th><th>Actions</th></tr></thead><tbody>';

                    data.items.forEach(resource => {
                        html += `<tr>
                            <td>${resource.id}</td>
                            <td>${resource.name}</td>
                            <td>${resource.year}</td>
                            <td><span style="background-color: ${resource.color}; padding: 2px 8px; color: white; border-radius: 3px;">${resource.color}</span></td>
                            <td>${resource.pantone_value}</td>
                            <td>
                                <button class="btn btn-sm btn-danger" onclick="deleteResource(${resource.id})">🗑️ Delete</button>
                            </td>
                        </tr>`;
                    });
                    html += '</tbody></table></div>';
                    document.getElementById('data-content').innerHTML = html;
                } catch (error) {
                    document.getElementById('data-content').innerHTML = '<div class="alert alert-danger">Error loading resources</div>';
                }
            }

            function showCreateUser() {
                document.getElementById('data-title').textContent = '➕ Create New User';
                const html = `
                    <form onsubmit="createUser(event)" class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label">Full Name</label>
                            <input type="text" class="form-control" name="name" required placeholder="John Doe">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Job Title</label>
                            <input type="text" class="form-control" name="job" required placeholder="Software Engineer">
                        </div>
                        <div class="col-12">
                            <button type="submit" class="btn btn-primary">Create User</button>
                            <button type="button" class="btn btn-secondary" onclick="loadUsers()">Cancel</button>
                        </div>
                    </form>
                `;
                document.getElementById('data-content').innerHTML = html;
            }

            function showCreateResource() {
                document.getElementById('data-title').textContent = '🎯 Create New Resource';
                const html = `
                    <form onsubmit="createResource(event)" class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label">Color Name</label>
                            <input type="text" class="form-control" name="name" required placeholder="Crimson Red">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Year</label>
                            <input type="number" class="form-control" name="year" required placeholder="2024">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Hex Color</label>
                            <input type="text" class="form-control" name="color" required placeholder="#DC143C">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Pantone Value</label>
                            <input type="text" class="form-control" name="pantone_value" required placeholder="19-1664">
                        </div>
                        <div class="col-12">
                            <button type="submit" class="btn btn-primary">Create Resource</button>
                            <button type="button" class="btn btn-secondary" onclick="loadResources()">Cancel</button>
                        </div>
                    </form>
                `;
                document.getElementById('data-content').innerHTML = html;
            }

            async function createUser(event) {
                event.preventDefault();
                const formData = new FormData(event.target);
                try {
                    const response = await fetch('/api/users', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            name: formData.get('name'),
                            job: formData.get('job')
                        })
                    });
                    if (response.ok) {
                        alert('✅ User created successfully!');
                        loadUsers();
                        loadStats();
                    } else {
                        alert('❌ Error creating user');
                    }
                } catch (error) {
                    alert('❌ Error: ' + error.message);
                }
            }

            async function createResource(event) {
                event.preventDefault();
                const formData = new FormData(event.target);
                try {
                    const response = await fetch('/api/resources', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            name: formData.get('name'),
                            year: parseInt(formData.get('year')),
                            color: formData.get('color'),
                            pantone_value: formData.get('pantone_value')
                        })
                    });
                    if (response.ok) {
                        alert('✅ Resource created successfully!');
                        loadResources();
                        loadStats();
                    } else {
                        alert('❌ Error creating resource');
                    }
                } catch (error) {
                    alert('❌ Error: ' + error.message);
                }
            }

            async function deleteUser(id) {
                if (confirm('Are you sure you want to delete this user?')) {
                    try {
                        const response = await fetch(`/api/users/${id}`, { method: 'DELETE' });
                        if (response.ok) {
                            alert('✅ User deleted successfully!');
                            loadUsers();
                            loadStats();
                        } else {
                            alert('❌ Error deleting user');
                        }
                    } catch (error) {
                        alert('❌ Error: ' + error.message);
                    }
                }
            }

            async function deleteResource(id) {
                if (confirm('Are you sure you want to delete this resource?')) {
                    try {
                        const response = await fetch(`/api/resources/${id}`, { method: 'DELETE' });
                        if (response.ok) {
                            alert('✅ Resource deleted successfully!');
                            loadResources();
                            loadStats();
                        } else {
                            alert('❌ Error deleting resource');
                        }
                    } catch (error) {
                        alert('❌ Error: ' + error.message);
                    }
                }
            }

            async function runTests() {
                document.getElementById('data-title').textContent = '🧪 API Testing';
                document.getElementById('data-content').innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div><p class="mt-2">Running API tests...</p></div>';

                setTimeout(() => {
                    const html = `
                        <div class="alert alert-info">
                            <h5>🧪 API Test Commands</h5>
                            <p>Run these commands in your terminal:</p>
                            <pre class="bg-dark text-light p-3 rounded">
# Test Users API
curl -X GET http://localhost:8000/api/users
curl -X POST http://localhost:8000/api/users -H "Content-Type: application/json" -d '{"name":"Test User","job":"Tester"}'

# Test Resources API  
curl -X GET http://localhost:8000/api/resources
curl -X POST http://localhost:8000/api/resources -H "Content-Type: application/json" -d '{"name":"Test Color","year":2024,"color":"#FF0000","pantone_value":"18-1664"}'

# Run Pytest Suite
poetry run pytest tests/ -v --alluredir=allure-results
poetry run allure serve allure-results
                            </pre>
                        </div>
                    `;
                    document.getElementById('data-content').innerHTML = html;
                }, 1000);
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)
