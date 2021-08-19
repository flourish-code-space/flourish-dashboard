from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_model_wrapper import ModelWrapper
from edc_base.utils import get_uuid
from edc_consent import ConsentModelWrapperMixin
from flourish_caregiver.models.subject_consent import SubjectConsent
from .bhp_prior_screening_model_wrapper_mixin import BHPPriorScreeningModelWrapperMixin
from .child_assent_model_wrapper_mixin import ChildAssentModelWrapperMixin
from .subject_consent_model_wrapper import SubjectConsentModelWrapper
from .antenatal_enrollment_wrapper_mixin import AntenatalEnrollmentModelWrapperMixin
from .caregiver_locator_model_wrapper_mixin import CaregiverLocatorModelWrapperMixin


class MaternalScreeningModelWrapper(AntenatalEnrollmentModelWrapperMixin,
                                    CaregiverLocatorModelWrapperMixin,
                                    ConsentModelWrapperMixin,
                                    ChildAssentModelWrapperMixin,
                                    BHPPriorScreeningModelWrapperMixin,
                                    ModelWrapper):
    consent_model_wrapper_cls = SubjectConsentModelWrapper
    model = 'flourish_caregiver.screeningpregwomen'
    querystring_attrs = ['screening_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'maternal_screening_listboard_url')
    next_url_attrs = ['screening_identifier', 'subject_identifier', ]

    @property
    def consent_version(self):
        return '1'

    @property
    def subject_identifier(self):
        if self.consent_model_obj:
            return self.consent_model_obj.subject_identifier
        return None

    @property
    def consent_model_obj(self):
        """Returns a consent model instance or None.
        """
        try:
            return self.subject_consent_cls.objects.get(**self.consent_options)
        except ObjectDoesNotExist:
            return None

    @property
    def subject_consent_cls(self):
        return django_apps.get_model('flourish_caregiver.subjectconsent')

    @property
    def create_consent_options(self):
        """Returns a dictionary of options to create a new
        unpersisted consent model instance.
        """
        options = dict(
            screening_identifier=self.screening_identifier,
            consent_identifier=get_uuid(),
            version=self.consent_version)
        return options

    @property
    def consent_options(self):
        """Returns a dictionary of options to get an existing
        consent model instance.
        """
        options = dict(
            screening_identifier=self.object.screening_identifier,
            version=self.consent_version)
        return options

    def is_eligible(self):
        return self.object.is_eligible

    def eligible_at_enrol(self):
        return self.object.is_eligible

    @property
    def study_maternal_identifier(self):
        if getattr(self, 'bhp_prior_screening_model_obj', None):
            return self.bhp_prior_screening_model_obj.study_maternal_identifier
        return ''

    @property
    def create_caregiver_locator_options(self):
        """
        Overrided the method to remove some of the functions to remove some the attr. not needed
        in this context

        Returns a dictionary of options to create a new
        unpersisted caregiver locator model instance.
        """

        # Get the current screening identifier
        screening_identifier = self.object.screening_identifier
        # Get the subject identifier using the screening identifier after consent
        subject_identifier = SubjectConsent.objects.get(screening_identifier=screening_identifier).subject_identifier

        options = dict(
            screening_identifier=screening_identifier,
            subject_identifier=subject_identifier,
        )
        if self.study_maternal_identifier and getattr(self, 'study_maternal_identifier'):
            options.update({'study_maternal_identifier': self.study_maternal_identifier})
        return options
