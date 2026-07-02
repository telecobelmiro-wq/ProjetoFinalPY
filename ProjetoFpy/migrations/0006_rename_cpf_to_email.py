from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ProjetoFpy', '0005_configuracao'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usuario',
            old_name='cpf',
            new_name='email',
        ),
        migrations.AlterField(
            model_name='usuario',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
