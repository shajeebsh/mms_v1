#!/usr/bin/env python
"""Grant basic model permissions to role groups.

Usage: python scripts/assign_group_permissions.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mms_site.settings')
import django
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

# mapping of group -> list of app_label.model names to grant permissions for
GROUP_MODEL_MAP = {
    'membership': [
        'membership.member', 'membership.family', 'membership.membershipdues', 'membership.payment'
    ],
    'finance': [
        'finance.donation', 'finance.expense', 'finance.financialreport', 'finance.donationcategory', 'finance.expensecategory'
    ],
    'education': [
        'education.teacher', 'education.class', 'education.studentenrollment'
    ],
    'assets': [
        'assets.shop', 'assets.propertyunit'
    ],
    'operations': [
        'operations.auditoriumbooking', 'operations.digitalsignagecontent', 'operations.prayertime'
    ],
    'hr': [
        'hr.staffmember', 'hr.staffposition', 'hr.payroll'
    ],
    'committee': [
        'committee.committee', 'committee.meeting', 'committee.trustee'
    ],
}

def grant_perms():
    for group_name, model_list in GROUP_MODEL_MAP.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        for model_path in model_list:
            try:
                app_label, model = model_path.split('.')
                ct = ContentType.objects.get(app_label=app_label, model=model.lower())
            except Exception as e:
                print(f"Skipping {model_path}: {e}")
                continue

            # grant add/change/delete/view permissions if they exist
            for codename_prefix in ('add_', 'change_', 'delete_', 'view_'):
                codename = f"{codename_prefix}{ct.model}"
                try:
                    perm = Permission.objects.get(content_type=ct, codename=codename)
                    group.permissions.add(perm)
                    print(f"Granted {codename} to {group_name}")
                except Permission.DoesNotExist:
                    # sometimes codename uses model name directly
                    try:
                        perm = Permission.objects.get(content_type=ct, codename=codename_prefix + model.lower())
                        group.permissions.add(perm)
                        print(f"Granted {perm.codename} to {group_name}")
                    except Permission.DoesNotExist:
                        print(f"Permission {codename} not found for {model_path}")


if __name__ == '__main__':
    grant_perms()
