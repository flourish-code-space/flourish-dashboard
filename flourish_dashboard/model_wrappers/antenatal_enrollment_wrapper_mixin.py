from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from .antenatal_enrollment_model_wrapper import AntenatalEnrollmentModelWrapper
from ..utils import flourish_dashboard_utils


class AntenatalEnrollmentModelWrapperMixin:
    antenatal_enrollment_model_wrapper_cls = AntenatalEnrollmentModelWrapper

    @property
    def antenatal_enrollment_model_obj(self):
        """Returns a antenatal enrollment model instance or None.
        """
        try:
            return self.antenatal_enrollment_cls.objects.get(
                **self.antenatal_enrollment_options)
        except ObjectDoesNotExist:
            return None

    @property
    def antenatal_enrollment(self):
        """Returns a wrapped saved or unsaved antenatal enrollment.
        """
        model_obj = self.antenatal_enrollment_model_obj or self.antenatal_enrollment_cls(
            **self.create_antenatal_enrollment_options)
        return self.antenatal_enrollment_model_wrapper_cls(model_obj=model_obj)

    @property
    def antenatal_enrollments(self):
        wrapped_entries = []
        if getattr(self, 'consent_model_obj', None):
            caregiver_child_consents = (
                self.consent_model_obj.caregiverchildconsent_set.all())

            for caregiver_child_consent in caregiver_child_consents:
                if flourish_dashboard_utils.screening_object_by_child_pid(
                        self.consent.screening_identifier,
                        caregiver_child_consent.subject_identifier):
                    model_obj = self.antenatal_enrollments_model_obj(
                        caregiver_child_consent) or self.antenatal_enrollment_cls(
                        **self.create_antenatal_enrollments_options(
                            caregiver_child_consent))
                    wrapped_entries.append(AntenatalEnrollmentModelWrapper(model_obj))

        return wrapped_entries

    @property
    def antenatal_enrollment_cls(self):
        return django_apps.get_model('flourish_caregiver.antenatalenrollment')

    @property
    def create_antenatal_enrollment_options(self):
        """Returns a dictionary of options to create a new
        unpersisted antenatal enrollment model instance.
        """
        options = dict(
            subject_identifier=self.consent.subject_identifier,
            # screening_identifier=self.consent.screening_identifier
        )
        return options

    @property
    def antenatal_enrollment_options(self):
        """Returns a dictionary of options to get an existing
        antenatal enrollment model instance.
        """
        options = dict(
            subject_identifier=self.consent.subject_identifier)
        return options

    @property
    def show_dashboard(self):
        return True

    def antenatal_enrollments_model_obj(self, caregiver_child_consent):
        try:
            return self.antenatal_enrollment_cls.objects.get(
                child_subject_identifier=caregiver_child_consent.subject_identifier,
                subject_identifier=self.consent.subject_identifier)
        except ObjectDoesNotExist:
            return None

    def create_antenatal_enrollments_options(self, caregiver_child_consent):
        options = dict(
            child_subject_identifier=caregiver_child_consent.subject_identifier,
            subject_identifier=self.consent.subject_identifier
        )
        return options
