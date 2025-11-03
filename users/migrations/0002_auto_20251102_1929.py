from django.db import migrations


def crear_datos_iniciales(apps, schema_editor):
    Empresa = apps.get_model('empresa', 'Empresa')
    Rol = apps.get_model('users', 'Rol')
    
    # Crear empresa default si no existe
    Empresa.objects.get_or_create(
        id_empresa=1,
        defaults={
            'nit': '860512330-3',
            'nombre_empresa': 'Servientrega',
            'telefono_empresa': '601 8889214'
        }
    )
    
    # Crear rol default si no existe
    Rol.objects.get_or_create(
        id_rol=1,
        defaults={'nombre_rol': 'driver'}
    )


def eliminar_datos_iniciales(apps, schema_editor):
    """Función para revertir la migración si es necesario"""
    Empresa = apps.get_model('empresa', 'Empresa')
    Rol = apps.get_model('users', 'Rol')
    
    Empresa.objects.filter(id_empresa=1).delete()
    Rol.objects.filter(id_rol=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('empresa', '0002_alter_empresa_nombre_empresa_and_more'),
    ]

    operations = [
        migrations.RunPython(crear_datos_iniciales, eliminar_datos_iniciales),
    ]
    