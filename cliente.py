import requests
import json
import sys
from getpass import getpass

# Configuración
BASE_URL = 'http://localhost:5000'
token = None


def mostrar_menu():
    """Muestra el menú principal"""
    print("\n" + "="*50)
    print("  ♦ SISTEMA DE GESTIÓN DE TAREAS ♦")
    print("="*50)
    if token:
        print("► Sesión activa")
    else:
        print("◄ No has iniciado sesión")
    print("\n--- Autenticación ---")
    print("1. Registrar nuevo usuario")
    print("2. Iniciar sesión")
    print("\n--- Gestión de Tareas ---")
    print("3. Ver mis tareas")
    print("4. Crear nueva tarea")
    print("5. Marcar tarea como completada")
    print("6. Actualizar tarea")
    print("7. Eliminar tarea")
    print("\n0. Salir")
    print("="*50)


def registrar_usuario():
    """Registra un nuevo usuario"""
    print("\n--- REGISTRO DE USUARIO ---")
    usuario = input("Usuario (mínimo 3 caracteres): ").strip()
    contraseña = getpass("Contraseña (mínimo 4 caracteres): ")
    
    try:
        response = requests.post(
            f'{BASE_URL}/registro',
            json={'usuario': usuario, 'contraseña': contraseña},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"\n► {data['mensaje']}")
            print(f"  Usuario: {data['usuario']}")
            print(f"  ID: {data['id']}")
        else:
            error = response.json().get('error', 'Error desconocido')
            print(f"\n◄ Error: {error}")
            
    except requests.exceptions.ConnectionError:
        print("\n◄ Error: No se puede conectar al servidor")
        print("  Asegúrate de que el servidor esté corriendo en http://localhost:5000")
    except Exception as e:
        print(f"\n◄ Error inesperado: {str(e)}")


def iniciar_sesion():
    """Inicia sesión y obtiene el token"""
    global token
    
    print("\n--- INICIAR SESIÓN ---")
    usuario = input("Usuario: ").strip()
    contraseña = getpass("Contraseña: ")
    
    try:
        response = requests.post(
            f'{BASE_URL}/login',
            json={'usuario': usuario, 'contraseña': contraseña},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data['token']
            print(f"\n► {data['mensaje']}")
            print(f"  Bienvenido, {data['usuario']}!")
            print(f"  Token: {token[:20]}...")
        else:
            error = response.json().get('error', 'Error desconocido')
            print(f"\n◄ Error: {error}")
            
    except requests.exceptions.ConnectionError:
        print("\n◄ Error: No se puede conectar al servidor")
    except Exception as e:
        print(f"\n◄ Error inesperado: {str(e)}")


def ver_tareas():
    """Muestra todas las tareas del usuario"""
    if not token:
        print("\n◄ Debes iniciar sesión primero")
        return
    
    try:
        response = requests.get(
            f'{BASE_URL}/tareas',
            headers={'Authorization': token}
        )
        
        if response.status_code == 200:
            data = response.json()
            tareas = data['tareas']
            
            print(f"\n--- MIS TAREAS ({data['total']}) ---")
            
            if not tareas:
                print("No tienes tareas registradas")
            else:
                for tarea in tareas:
                    estado = "•" if tarea['completada'] else "○"
                    print(f"\n{estado} ID: {tarea['id']}")
                    print(f"  Título: {tarea['titulo']}")
                    if tarea['descripcion']:
                        print(f"  Descripción: {tarea['descripcion']}")
                    print(f"  Creada: {tarea['fecha_creacion']}")
        else:
            error = response.json().get('error', 'Error desconocido')
            print(f"\n◄ Error: {error}")
            
    except requests.exceptions.ConnectionError:
        print("\n◄ Error: No se puede conectar al servidor")
    except Exception as e:
        print(f"\n◄ Error inesperado: {str(e)}")


def crear_tarea():
    """Crea una nueva tarea"""
    if not token:
        print("\n◄ Debes iniciar sesión primero")
        return
    
    print("\n--- CREAR NUEVA TAREA ---")
    titulo = input("Título: ").strip()
    descripcion = input("Descripción (opcional): ").strip()
    
    if not titulo:
        print("◄ El título no puede estar vacío")
        return
    
    try:
        response = requests.post(
            f'{BASE_URL}/tareas',
            json={'titulo': titulo, 'descripcion': descripcion},
            headers={
                'Authorization': token,
                'Content-Type': 'application/json'
            }
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"\n► {data['mensaje']}")
            print(f"  ID: {data['id']}")
            print(f"  Título: {data['titulo']}")
        else:
            error = response.json().get('error', 'Error desconocido')
            print(f"\n◄ Error: {error}")
            
    except requests.exceptions.ConnectionError:
        print("\n◄ Error: No se puede conectar al servidor")
    except Exception as e:
        print(f"\n◄ Error inesperado: {str(e)}")


def marcar_completada():
    """Marca una tarea como completada"""
    if not token:
        print("\n◄ Debes iniciar sesión primero")
        return
    
    try:
        tarea_id = int(input("\nID de la tarea a completar: "))
        
        response = requests.put(
            f'{BASE_URL}/tareas/{tarea_id}',
            json={'completada': True},
            headers={
                'Authorization': token,
                'Content-Type': 'application/json'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n► {data['mensaje']}")
        else:
            error = response.json().get('error', 'Error desconocido')
            print(f"\n◄ Error: {error}")
            
    except ValueError:
        print("\n◄ ID inválido")
    except requests.exceptions.ConnectionError:
        print("\n◄ Error: No se puede conectar al servidor")
    except Exception as e:
        print(f"\n◄ Error inesperado: {str(e)}")


def actualizar_tarea():
    """Actualiza una tarea existente"""
    if not token:
        print("\n◄ Debes iniciar sesión primero")
        return
    
    try:
        tarea_id = int(input("\nID de la tarea a actualizar: "))
        
        print("\nDeja en blanco los campos que no quieras modificar")
        titulo = input("Nuevo título: ").strip()
        descripcion = input("Nueva descripción: ").strip()
        completada = input("¿Completada? (s/n): ").lower().strip()
        
        datos = {}
        if titulo:
            datos['titulo'] = titulo
        if descripcion:
            datos['descripcion'] = descripcion
        if completada in ['s', 'n']:
            datos['completada'] = completada == 's'
        
        if not datos:
            print("\n◄ No hay cambios para aplicar")
            return
        
        response = requests.put(
            f'{BASE_URL}/tareas/{tarea_id}',
            json=datos,
            headers={
                'Authorization': token,
                'Content-Type': 'application/json'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n► {data['mensaje']}")
        else:
            error = response.json().get('error', 'Error desconocido')
            print(f"\n◄ Error: {error}")
            
    except ValueError:
        print("\n◄ ID inválido")
    except requests.exceptions.ConnectionError:
        print("\n◄ Error: No se puede conectar al servidor")
    except Exception as e:
        print(f"\n◄ Error inesperado: {str(e)}")


def eliminar_tarea():
    """Elimina una tarea"""
    if not token:
        print("\n◄ Debes iniciar sesión primero")
        return
    
    try:
        tarea_id = int(input("\nID de la tarea a eliminar: "))
        confirmacion = input(f"¿Estás seguro de eliminar la tarea {tarea_id}? (s/n): ")
        
        if confirmacion.lower() != 's':
            print("Operación cancelada")
            return
        
        response = requests.delete(
            f'{BASE_URL}/tareas/{tarea_id}',
            headers={'Authorization': token}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n◄ {data['mensaje']}")
        else:
            error = response.json().get('error', 'Error desconocido')
            print(f"\n► Error: {error}")
            
    except ValueError:
        print("\n◄ ID inválido")
    except requests.exceptions.ConnectionError:
        print("\n◄ Error: No se puede conectar al servidor")
    except Exception as e:
        print(f"\n◄ Error inesperado: {str(e)}")


def main():
    """Función principal del cliente"""
    print("\n♦ Cliente de Gestión de Tareas ♦")
    print("Conectando a:", BASE_URL)
    
    while True:
        mostrar_menu()
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == '1':
            registrar_usuario()
        elif opcion == '2':
            iniciar_sesion()
        elif opcion == '3':
            ver_tareas()
        elif opcion == '4':
            crear_tarea()
        elif opcion == '5':
            marcar_completada()
        elif opcion == '6':
            actualizar_tarea()
        elif opcion == '7':
            eliminar_tarea()
        elif opcion == '0':
            print("\n♦ ¡Hasta luego! ♦")
            sys.exit(0)
        else:
            print("\n◄ Opción inválida")
        
        input("\nPresiona Enter para continuar...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n♦ ¡Hasta luego! ♦")
        sys.exit(0)