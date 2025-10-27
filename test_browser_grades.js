// Test de funcionalidad de grados - Para ejecutar en consola del navegador
// Asegúrate de estar en la página: http://localhost:8000/administration/system-config/

console.log("=== INICIANDO PRUEBAS DE GRADOS ===");

// Función para probar la carga de grados
function testLoadGrades() {
    console.log("\n1. PROBANDO CARGA DE GRADOS...");
    
    return fetch('/academic-system/api/grades/')
        .then(response => {
            console.log('Status:', response.status);
            console.log('Content-Type:', response.headers.get('content-type'));
            return response.json();
        })
        .then(data => {
            console.log('✅ Datos recibidos:', data);
            console.log(`Número de grados: ${data.count}`);
            return data;
        })
        .catch(error => {
            console.error('❌ Error:', error);
        });
}

// Función para probar creación de grado
function testCreateGrade() {
    console.log("\n2. PROBANDO CREACIÓN DE GRADO...");
    
    const testData = {
        name: 'Grado Test',
        level: 'primaria',
        order: 99
    };
    
    // Obtener el token CSRF de la página
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                     document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    
    console.log('Token CSRF:', csrfToken ? 'Encontrado' : 'No encontrado');
    console.log('Datos a enviar:', testData);
    
    return fetch('/academic-system/api/grades/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(testData)
    })
    .then(response => {
        console.log('Status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('✅ Respuesta de creación:', data);
        return data;
    })
    .catch(error => {
        console.error('❌ Error en creación:', error);
    });
}

// Función para probar eliminación (si se creó el grado de prueba)
function testDeleteGrade(gradeId) {
    console.log(`\n3. PROBANDO ELIMINACIÓN DE GRADO ID: ${gradeId}...`);
    
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                     document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    
    return fetch(`/academic-system/api/grades/${gradeId}/delete/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        console.log('Status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('✅ Respuesta de eliminación:', data);
        return data;
    })
    .catch(error => {
        console.error('❌ Error en eliminación:', error);
    });
}

// Probar si las funciones de la página existen
function testPageFunctions() {
    console.log("\n4. PROBANDO FUNCIONES DE LA PÁGINA...");
    
    console.log('loadGrades existe:', typeof loadGrades !== 'undefined');
    console.log('openGradeModal existe:', typeof openGradeModal !== 'undefined');
    console.log('saveGrade existe:', typeof saveGrade !== 'undefined');
    console.log('deleteGrade existe:', typeof deleteGrade !== 'undefined');
    
    // Si loadGrades existe, probarla
    if (typeof loadGrades !== 'undefined') {
        console.log('Ejecutando loadGrades()...');
        loadGrades();
    }
}

// Ejecutar todas las pruebas
async function runAllTests() {
    console.log("=== EJECUTANDO TODAS LAS PRUEBAS ===");
    
    try {
        // Test 1: Cargar grados
        const gradesData = await testLoadGrades();
        
        // Test 2: Funciones de página
        testPageFunctions();
        
        // Test 3: Crear grado de prueba
        const createResult = await testCreateGrade();
        
        // Test 4: Si se creó correctamente, eliminarlo
        if (createResult && createResult.status === 'success' && createResult.data?.id) {
            console.log('Grado de prueba creado, eliminándolo...');
            await testDeleteGrade(createResult.data.id);
        }
        
        console.log("\n=== PRUEBAS COMPLETADAS ===");
        
    } catch (error) {
        console.error('Error en las pruebas:', error);
    }
}

// Instrucciones para ejecutar
console.log(`
INSTRUCCIONES:
1. Abre la página: http://localhost:8000/administration/system-config/
2. Haz login como admin
3. Abre la consola del desarrollador (F12)
4. Pega este código completo
5. Ejecuta: runAllTests()

O ejecuta las funciones individuales:
- testLoadGrades()
- testPageFunctions()
- testCreateGrade()
`);

// Auto-ejecutar si se pega en consola
if (typeof window !== 'undefined') {
    console.log("Script cargado. Ejecuta runAllTests() para probar todo.");
}