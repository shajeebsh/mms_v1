
import pytest
from education.models import Class, StudentEnrollment, StudentFeePayment, Teacher
from membership.models import Member
from accounting.models import Transaction, JournalEntry, Account

@pytest.mark.django_db
class TestEducationFees:
    @pytest.fixture
    def setup_data(self):
        # Create Teacher
        teacher = Teacher.objects.create(name="Test Teacher")
        
        # Create Class with Fee
        class_obj = Class.objects.create(
            name="Python 101",
            grade_level="secondary",
            subject="computer_science",
            teacher=teacher,
            course_fee=1000.00
        )
        
        # Create Student (Member)
        # Create House items
        from membership.models import HouseRegistration, Ward, Taluk, City, State, Country, PostalCode
        # Need to create FK dependencies first... this is getting heavy. 
        # But wait, Member validation might run? 
        # Let's bypass validation by using .save() if needed, but create() calls clean() only if forced? No, create() doesn't call clean().
        # However, db constraints might apply.
        
        # Simplified creation for test (assuming no strict DB constraints on FKs if sqlite/mocked or just create them)
        # Actually in pytest-django with sqlite, constraints exist.
        
        # NOTE: The previous failure "super..." happened BEFORE "Unexpected keyword arg".
        # This implies the super error happens super early.
        
        student = Member.objects.create(
            first_name="John",
            last_name="Doe",
            phone="1234567890",
            gender="M"
        )
        
        return {'class': class_obj, 'student': student}

    def test_enrollment_initial_status(self, setup_data):
        enrollment = StudentEnrollment.objects.create(
            student=setup_data['student'],
            class_instance=setup_data['class']
        )
        
        assert enrollment.payment_status == 'pending'
        assert enrollment.total_paid == 0
        assert enrollment.balance_amount == 1000.00

    def test_partial_payment(self, setup_data):
        enrollment = StudentEnrollment.objects.create(
            student=setup_data['student'],
            class_instance=setup_data['class']
        )
        
        payment = StudentFeePayment.objects.create(
            enrollment=enrollment,
            amount=500.00,
            payment_method='cash'
        )
        
        # Refresh from DB
        enrollment.refresh_from_db()
        
        assert enrollment.payment_status == 'partial'
        assert enrollment.total_paid == 500.00
        assert enrollment.balance_amount == 500.00

    def test_full_payment(self, setup_data):
        enrollment = StudentEnrollment.objects.create(
            student=setup_data['student'],
            class_instance=setup_data['class']
        )
        
        payment = StudentFeePayment.objects.create(
            enrollment=enrollment,
            amount=1000.00,
            payment_method='cash'
        )
        
        enrollment.refresh_from_db()
        
        assert enrollment.payment_status == 'paid'
        assert enrollment.total_paid == 1000.00
        assert enrollment.balance_amount == 0.00

    def test_accounting_entry_creation(self, setup_data):
        enrollment = StudentEnrollment.objects.create(
            student=setup_data['student'],
            class_instance=setup_data['class']
        )
        
        # Creating payment should trigger signal
        payment = StudentFeePayment.objects.create(
            enrollment=enrollment,
            amount=500.00,
            payment_method='cash'
        )
        
        # Check Transaction
        transaction = Transaction.objects.last()
        assert transaction is not None
        assert "Course Fee" in transaction.description
        assert str(enrollment.student.full_name) in transaction.description
        
        # Check Journal Entries
        entries = JournalEntry.objects.filter(transaction=transaction)
        assert entries.count() == 2
        
        debit_entry = entries.filter(debit__gt=0).first()
        credit_entry = entries.filter(credit__gt=0).first()
        
        assert debit_entry.account.name == "Cash in Hand"
        assert debit_entry.debit == 500.00
        
        assert credit_entry.account.name == "Education Fees"
        assert credit_entry.credit == 500.00
