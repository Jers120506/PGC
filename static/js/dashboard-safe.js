// Script para manejar elementos dinámicos en templates Django
// Evita errores de sintaxis en Visual Studio Code

document.addEventListener('DOMContentLoaded', function() {
    
    // ========================================
    // PROGRESS BARS - Establecer ancho dinámico
    // ========================================
    function initializeProgressBars() {
        // Progress bars con clase project-progress-bar
        document.querySelectorAll('.project-progress-bar').forEach(bar => {
            const progress = bar.getAttribute('data-progress');
            if (progress) {
                bar.style.width = progress + '%';
            }
        });
        
        // Progress bars genéricos con data-progress
        document.querySelectorAll('[data-progress]').forEach(element => {
            if (element.classList.contains('progress-bar')) {
                const progress = element.getAttribute('data-progress');
                if (progress) {
                    element.style.width = progress + '%';
                }
            }
        });
    }
    
    // ========================================
    // CHARTS - Configurar Chart.js con datos seguros
    // ========================================
    function initializeCharts() {
        // Progress Chart (Doughnut)
        const progressChartElement = document.getElementById('progressChart');
        if (progressChartElement) {
            const chartData = {
                completed: parseInt(progressChartElement.getAttribute('data-completed') || 0),
                inProgress: parseInt(progressChartElement.getAttribute('data-in-progress') || 0),
                pending: parseInt(progressChartElement.getAttribute('data-pending') || 0)
            };
            
            new Chart(progressChartElement, {
                type: 'doughnut',
                data: {
                    labels: ['Completadas', 'En Progreso', 'Pendientes'],
                    datasets: [{
                        data: [chartData.completed, chartData.inProgress, chartData.pending],
                        backgroundColor: ['#28a745', '#007bff', '#ffc107'],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                boxWidth: 12,
                                font: { size: 12 }
                            }
                        }
                    }
                }
            });
        }
        
        // Otros charts pueden ir aquí
        const reportsChartElement = document.getElementById('reportsChart');
        if (reportsChartElement) {
            const reportsData = {
                completed: parseInt(reportsChartElement.getAttribute('data-completed') || 0),
                inProgress: parseInt(reportsChartElement.getAttribute('data-in-progress') || 0),
                review: parseInt(reportsChartElement.getAttribute('data-review') || 0),
                pending: parseInt(reportsChartElement.getAttribute('data-pending') || 0)
            };
            
            new Chart(reportsChartElement, {
                type: 'doughnut',
                data: {
                    labels: ['Completados', 'En Progreso', 'En Revisión', 'Pendientes'],
                    datasets: [{
                        data: [reportsData.completed, reportsData.inProgress, reportsData.review, reportsData.pending],
                        backgroundColor: ['#28a745', '#007bff', '#ffc107', '#6c757d'],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                boxWidth: 12,
                                font: { size: 12 }
                            }
                        }
                    }
                }
            });
        }
    }
    
    // ========================================
    // BUTTONS - Event handlers seguros
    // ========================================
    function initializeButtons() {
        // Task toggle buttons
        document.querySelectorAll('.task-toggle-btn').forEach(button => {
            button.addEventListener('click', function() {
                const taskId = this.getAttribute('data-task-id');
                if (taskId && confirm('¿Marcar esta tarea como completada?')) {
                    // Aquí se haría la llamada AJAX real
                    window.location.reload();
                }
            });
        });
        
        // Milestone toggle buttons
        document.querySelectorAll('.milestone-toggle').forEach(button => {
            button.addEventListener('click', function() {
                const milestoneId = this.getAttribute('data-milestone-id');
                if (milestoneId && confirm('¿Marcar este hito como completado?')) {
                    // Aquí se haría la llamada AJAX real
                    window.location.reload();
                }
            });
        });
        
        // Feedback buttons
        document.querySelectorAll('.feedback-btn').forEach(button => {
            button.addEventListener('click', function() {
                const projectId = this.getAttribute('data-project-id');
                if (projectId) {
                    alert('Función de feedback para proyecto ID: ' + projectId);
                    // Aquí se implementaría el modal o formulario de feedback
                }
            });
        });
    }
    
    // ========================================
    // LIVE UPDATES - Auto-refresh para elementos dinámicos
    // ========================================
    function initializeLiveUpdates() {
        // Auto-refresh para tareas en progreso (cada 30 segundos)
        const inProgressTasks = document.querySelectorAll('.task-status.in_progress');
        if (inProgressTasks.length > 0) {
            setInterval(function() {
                // Aquí se podrían hacer llamadas AJAX para actualizar estados
                console.log('Checking for task updates...');
            }, 30000);
        }
    }
    
    // ========================================
    // INICIALIZACIÓN
    // ========================================
    initializeProgressBars();
    initializeCharts();
    initializeButtons();
    initializeLiveUpdates();
    
    console.log('✅ Dashboard scripts initialized successfully');
});

// ========================================
// FUNCIONES GLOBALES (para compatibilidad)
// ========================================
function toggleTaskStatus(taskId) {
    if (confirm('¿Marcar esta tarea como completada?')) {
        window.location.reload();
    }
}

function toggleMilestone(milestoneId) {
    if (confirm('¿Marcar este hito como completado?')) {
        window.location.reload();
    }
}

function sendFeedback(projectId) {
    alert('Enviando feedback para proyecto ID: ' + projectId);
    // Implementar modal o formulario de feedback
}