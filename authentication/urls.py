from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Autenticación básica
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    # path('register/', views.RegisterView.as_view(), name='register'),  # Deshabilitado - Solo admins pueden crear usuarios
    
    # Recuperación de contraseña
    path('password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # Perfil de usuario
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # Administración de usuarios (solo para administradores)
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin/create-user/', views.AdminCreateUserView.as_view(), name='admin_create_user'),
    path('admin/create-student/', views.AdminCreateStudentView.as_view(), name='admin_create_student'),
    path('admin/users/', views.UserListView.as_view(), name='user_list'),
    path('admin/edit-user/<int:user_id>/', views.AdminEditUserView.as_view(), name='admin_edit_user'),
    path('admin/delete-user/<int:user_id>/', views.AdminDeleteUserView.as_view(), name='admin_delete_user'),
    path('admin/assign-students/', views.AssignStudentsView.as_view(), name='assign_students'),
    path('admin/unassign-students/<int:teacher_id>/', views.UnassignStudentsView.as_view(), name='unassign_students'),
]