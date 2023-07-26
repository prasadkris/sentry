# Generated by Django 4.2.3 on 2023-07-28 18:36

from django.db import migrations

from sentry.new_migrations.migrations import CheckedMigration


class Migration(CheckedMigration):
    # This flag is used to mark that a migration shouldn't be automatically run in production. For
    # the most part, this should only be used for operations where it's safe to run the migration
    # after your code has deployed. So this should not be used for most operations that alter the
    # schema of a table.
    # Here are some things that make sense to mark as dangerous:
    # - Large data migrations. Typically we want these to be run manually by ops so that they can
    #   be monitored and not block the deploy for a long period of time while they run.
    # - Adding indexes to large tables. Since this can take a long time, we'd generally prefer to
    #   have ops run this and not block the deploy. Note that while adding an index is a schema
    #   change, it's completely safe to run the operation after the code has deployed.
    is_dangerous = False

    dependencies = [
        ("sentry", "0525_add_next_checkin_latest"),
    ]

    operations = [
        migrations.RenameIndex(
            model_name="activity",
            new_name="sentry_acti_project_cd8457_idx",
            old_fields=("project", "datetime"),
        ),
        migrations.RenameIndex(
            model_name="artifactbundleflatfileindex",
            new_name="sentry_arti_project_a4b244_idx",
            old_fields=("project_id", "release_name", "dist_name"),
        ),
        migrations.RenameIndex(
            model_name="artifactbundleindex",
            new_name="sentry_arti_url_7e628a_idx",
            old_fields=("url", "artifact_bundle"),
        ),
        migrations.RenameIndex(
            model_name="commit",
            new_name="sentry_comm_reposit_da31f2_idx",
            old_fields=("repository_id", "date_added"),
        ),
        migrations.RenameIndex(
            model_name="controloutbox",
            new_name="sentry_cont_region__1c1c72_idx",
            old_fields=(
                "region_name",
                "shard_scope",
                "shard_identifier",
                "category",
                "object_identifier",
            ),
        ),
        migrations.RenameIndex(
            model_name="controloutbox",
            new_name="sentry_cont_region__a95d82_idx",
            old_fields=("region_name", "shard_scope", "shard_identifier", "id"),
        ),
        migrations.RenameIndex(
            model_name="controloutbox",
            new_name="sentry_cont_region__0c4512_idx",
            old_fields=("region_name", "shard_scope", "shard_identifier", "scheduled_for"),
        ),
        migrations.RenameIndex(
            model_name="debugidartifactbundle",
            new_name="sentry_debu_debug_i_8c6c44_idx",
            old_fields=("debug_id", "artifact_bundle"),
        ),
        migrations.RenameIndex(
            model_name="eventattachment",
            new_name="sentry_even_project_62b83b_idx",
            old_fields=("project_id", "date_added"),
        ),
        migrations.RenameIndex(
            model_name="eventattachment",
            new_name="sentry_even_project_3a35bc_idx",
            old_fields=("project_id", "date_added", "file_id"),
        ),
        migrations.RenameIndex(
            model_name="eventuser",
            new_name="sentry_even_project_af92d2_idx",
            old_fields=("project_id", "ip_address"),
        ),
        migrations.RenameIndex(
            model_name="eventuser",
            new_name="sentry_even_project_51a6f0_idx",
            old_fields=("project_id", "username"),
        ),
        migrations.RenameIndex(
            model_name="eventuser",
            new_name="sentry_even_project_b7cf3d_idx",
            old_fields=("project_id", "email"),
        ),
        migrations.RenameIndex(
            model_name="group",
            new_name="sentry_grou_project_ff3fdf_idx",
            old_fields=("project", "status", "substatus", "type", "last_seen", "id"),
        ),
        migrations.RenameIndex(
            model_name="group",
            new_name="sentry_grou_project_4662d9_idx",
            old_fields=("project", "first_release"),
        ),
        migrations.RenameIndex(
            model_name="group",
            new_name="sentry_grou_project_5eb75b_idx",
            old_fields=("project", "status", "substatus", "last_seen", "id"),
        ),
        migrations.RenameIndex(
            model_name="group",
            new_name="sentry_grou_project_17d28d_idx",
            old_fields=("project", "status", "type", "last_seen", "id"),
        ),
        migrations.RenameIndex(
            model_name="group",
            new_name="sentry_grou_project_41a5ce_idx",
            old_fields=("project", "id"),
        ),
        migrations.RenameIndex(
            model_name="group",
            new_name="sentry_grou_project_5acaf7_idx",
            old_fields=("project", "status", "substatus", "id"),
        ),
        migrations.RenameIndex(
            model_name="group",
            new_name="sentry_grou_project_81a5ed_idx",
            old_fields=("project", "status", "last_seen", "id"),
        ),
        migrations.RenameIndex(
            model_name="groupenvironment",
            new_name="sentry_grou_environ_6f7f28_idx",
            old_fields=("environment", "first_release"),
        ),
        migrations.RenameIndex(
            model_name="grouphistory",
            new_name="sentry_grou_group_i_c61acb_idx",
            old_fields=("group", "status"),
        ),
        migrations.RenameIndex(
            model_name="grouphistory",
            new_name="sentry_grou_project_20b3f8_idx",
            old_fields=("project", "date_added"),
        ),
        migrations.RenameIndex(
            model_name="grouphistory",
            new_name="sentry_grou_project_bbcf30_idx",
            old_fields=("project", "status", "release"),
        ),
        migrations.RenameIndex(
            model_name="groupinbox",
            new_name="sentry_grou_project_a9fe16_idx",
            old_fields=("project", "date_added"),
        ),
        migrations.RenameIndex(
            model_name="grouprelease",
            new_name="sentry_grou_group_i_f10abe_idx",
            old_fields=("group_id", "last_seen"),
        ),
        migrations.RenameIndex(
            model_name="grouprelease",
            new_name="sentry_grou_group_i_6eaff8_idx",
            old_fields=("group_id", "first_seen"),
        ),
        migrations.RenameIndex(
            model_name="incident",
            new_name="sentry_inci_alert_r_24a457_idx",
            old_fields=("alert_rule", "type", "status"),
        ),
        migrations.RenameIndex(
            model_name="organizationmembermapping",
            new_name="sentry_orga_organiz_7de26b_idx",
            old_fields=("organization_id", "email"),
        ),
        migrations.RenameIndex(
            model_name="organizationmembermapping",
            new_name="sentry_orga_organiz_ae9fe7_idx",
            old_fields=("organization_id", "user"),
        ),
        migrations.RenameIndex(
            model_name="projectartifactbundle",
            new_name="sentry_proj_project_f73d36_idx",
            old_fields=("project_id", "artifact_bundle"),
        ),
        migrations.RenameIndex(
            model_name="projectdebugfile",
            new_name="sentry_proj_project_9b5950_idx",
            old_fields=("project_id", "code_id"),
        ),
        migrations.RenameIndex(
            model_name="projectdebugfile",
            new_name="sentry_proj_project_c586ac_idx",
            old_fields=("project_id", "debug_id"),
        ),
        migrations.RenameIndex(
            model_name="pullrequest",
            new_name="sentry_pull_organiz_8aabcf_idx",
            old_fields=("organization_id", "merge_commit_sha"),
        ),
        migrations.RenameIndex(
            model_name="pullrequest",
            new_name="sentry_pull_reposit_c429a4_idx",
            old_fields=("repository_id", "date_added"),
        ),
        migrations.RenameIndex(
            model_name="regionoutbox",
            new_name="sentry_regi_shard_s_cd9995_idx",
            old_fields=("shard_scope", "shard_identifier", "scheduled_for"),
        ),
        migrations.RenameIndex(
            model_name="regionoutbox",
            new_name="sentry_regi_shard_s_bfff84_idx",
            old_fields=("shard_scope", "shard_identifier", "category", "object_identifier"),
        ),
        migrations.RenameIndex(
            model_name="regionoutbox",
            new_name="sentry_regi_shard_s_e7412f_idx",
            old_fields=("shard_scope", "shard_identifier", "id"),
        ),
        migrations.RenameIndex(
            model_name="release",
            new_name="sentry_rele_organiz_6b035f_idx",
            old_fields=("organization", "build_number"),
        ),
        migrations.RenameIndex(
            model_name="release",
            new_name="sentry_rele_organiz_ffeeb2_idx",
            old_fields=("organization", "build_code"),
        ),
        migrations.RenameIndex(
            model_name="release",
            new_name="sentry_rele_organiz_23ee54_idx",
            old_fields=(
                "organization",
                "package",
                "major",
                "minor",
                "patch",
                "revision",
                "prerelease",
            ),
        ),
        migrations.RenameIndex(
            model_name="release",
            new_name="sentry_rele_organiz_71087c_idx",
            old_fields=("organization", "major", "minor", "patch", "revision", "prerelease"),
        ),
        migrations.RenameIndex(
            model_name="release",
            new_name="sentry_rele_organiz_6975e7_idx",
            old_fields=("organization", "status"),
        ),
        migrations.RenameIndex(
            model_name="release",
            new_name="sentry_rele_organiz_4ed947_idx",
            old_fields=("organization", "date_added"),
        ),
        migrations.RenameIndex(
            model_name="releaseartifactbundle",
            new_name="sentry_rele_organiz_291018_idx",
            old_fields=("organization_id", "release_name", "dist_name", "artifact_bundle"),
        ),
        migrations.RenameIndex(
            model_name="releasefile",
            new_name="sentry_rele_release_bff97c_idx",
            old_fields=("release_id", "name"),
        ),
        migrations.RenameIndex(
            model_name="releaseproject",
            new_name="sentry_rele_project_3143eb_idx",
            old_fields=("project", "first_seen_transaction"),
        ),
        migrations.RenameIndex(
            model_name="releaseproject",
            new_name="sentry_rele_project_2ca122_idx",
            old_fields=("project", "unadopted"),
        ),
        migrations.RenameIndex(
            model_name="releaseproject",
            new_name="sentry_rele_project_a80825_idx",
            old_fields=("project", "adopted"),
        ),
        migrations.RenameIndex(
            model_name="releaseprojectenvironment",
            new_name="sentry_rele_project_4bea8e_idx",
            old_fields=("project", "adopted", "environment"),
        ),
        migrations.RenameIndex(
            model_name="releaseprojectenvironment",
            new_name="sentry_rele_project_922a6a_idx",
            old_fields=("project", "unadopted", "environment"),
        ),
        migrations.RenameIndex(
            model_name="rule",
            new_name="sentry_rule_project_676d0d_idx",
            old_fields=("project", "status", "owner"),
        ),
        migrations.RenameIndex(
            model_name="userreport",
            new_name="sentry_user_project_cbfd59_idx",
            old_fields=("project_id", "event_id"),
        ),
        migrations.RenameIndex(
            model_name="userreport",
            new_name="sentry_user_project_b8faaf_idx",
            old_fields=("project_id", "date_added"),
        ),
    ]
