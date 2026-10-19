from django.db import migrations


def convert_comment_table(apps, schema_editor):
    if schema_editor.connection.vendor != "mysql":
        return
    schema_editor.execute(
        "ALTER TABLE blog_comment "
        "CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )


class Migration(migrations.Migration):
    # MariaDB は DDL をロールバックできない。トランザクション内の ALTER は拒否される。
    atomic = False

    dependencies = [
        ("blog", "0004_comment"),
    ]

    operations = [
        migrations.RunPython(convert_comment_table, migrations.RunPython.noop),
    ]
