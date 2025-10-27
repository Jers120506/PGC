// Script para abrir la página de login y luego el sistema de horarios
// Ejecutar en la consola del navegador

console.log("🔐 Verificando autenticación para sistema de horarios");

// Función para verificar estado de login
async function checkAuthStatus() {
    try {
        // Intentar acceder a la API de recursos
        const response = await fetch('/academic-system/schedules/resources/', {
            method: 'GET',
            credentials: 'same-origin'
        });
        
        console.log(`📡 Status de API: ${response.status}`);
        
        if (response.status === 200) {
            const data = await response.json();
            if (data.status === 'success') {
                console.log("✅ Usuario autenticado correctamente");
                console.log("📊 Recursos disponibles:", {
                    courses: data.data.courses?.length || 0,
                    teachers: data.data.teachers?.length || 0,
                    classrooms: data.data.classrooms?.length || 0,
                    subjects: data.data.subjects?.length || 0,
                    time_slots: data.data.time_slots?.length || 0
                });
                return true;
            }
        } else if (response.status === 302 || response.status === 401) {
            console.log("❌ Usuario no autenticado - Se requiere login");
            return false;
        } else if (response.status === 403) {
            console.log("❌ Usuario autenticado pero sin permisos");
            return false;
        }
    } catch (error) {
        console.error("💥 Error verificando autenticación:", error);
        return false;
    }
}

// Función para hacer login automático
async function autoLogin() {
    try {
        console.log("🔄 Intentando login automático...");
        
        // Obtener página de login
        const loginPage = await fetch('/auth/login/');
        const loginHtml = await loginPage.text();
        
        // Extraer CSRF token
        const csrfMatch = loginHtml.match(/name=['"]*csrfmiddlewaretoken['"]*\s+value=['"]*([^'"]+)/);
        if (!csrfMatch) {
            console.error("❌ No se pudo obtener CSRF token");
            return false;
        }
        
        const csrfToken = csrfMatch[1];
        console.log("✅ CSRF token obtenido");
        
        // Hacer login
        const formData = new FormData();
        formData.append('username', 'admin');
        formData.append('password', 'admin123');
        formData.append('csrfmiddlewaretoken', csrfToken);
        
        const loginResponse = await fetch('/auth/login/', {
            method: 'POST',
            body: formData,
            credentials: 'same-origin'
        });
        
        console.log(`📡 Login response: ${loginResponse.status}`);
        
        if (loginResponse.ok || loginResponse.status === 302) {
            console.log("✅ Login exitoso");
            return true;
        } else {
            console.log("❌ Login fallido");
            return false;
        }
        
    } catch (error) {
        console.error("💥 Error en login automático:", error);
        return false;
    }
}

// Función principal
async function setupScheduleSystem() {
    console.log("🚀 Configurando sistema de horarios...");
    
    // 1. Verificar autenticación actual
    const isAuthenticated = await checkAuthStatus();
    
    if (!isAuthenticated) {
        console.log("🔐 Realizando login...");
        const loginSuccess = await autoLogin();
        
        if (loginSuccess) {
            // Verificar de nuevo después del login
            await new Promise(resolve => setTimeout(resolve, 1000)); // Esperar 1 segundo
            const isNowAuthenticated = await checkAuthStatus();
            
            if (isNowAuthenticated) {
                console.log("🎉 ¡Sistema listo! Puedes crear horarios ahora.");
                console.log("📍 Ve a: http://127.0.0.1:8000/academic-system/schedules/");
            } else {
                console.log("❌ Aún hay problemas de autenticación");
            }
        } else {
            console.log("❌ No se pudo realizar el login automático");
            console.log("💡 Ve manualmente a: http://127.0.0.1:8000/auth/login/");
            console.log("🔑 Usuario: admin, Contraseña: admin123");
        }
    } else {
        console.log("🎉 ¡Usuario ya autenticado! Sistema listo.");
    }
}

// Ejecutar configuración
setupScheduleSystem();