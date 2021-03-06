from collections import OrderedDict
from datetime import timedelta

from django.core.urlresolvers import reverse
from django.utils import timezone

from bulbs.super_features.models import (
    BaseSuperFeature, GUIDE_TO_HOMEPAGE, GUIDE_TO_ENTRY
)
from bulbs.utils.test import BaseAPITestCase


class SuperFeatureViewsTestCase(BaseAPITestCase):

    def setUp(self):
        super(SuperFeatureViewsTestCase, self).setUp()
        self.parent = BaseSuperFeature.objects.create(
            title="Guide to Cats",
            notes="This is the guide to cats",
            superfeature_type=GUIDE_TO_HOMEPAGE,
            data={
                "sponsor_text": "Fancy Feast",
                "sponsor_image": {"id": 1}
            }
        )
        self.child = BaseSuperFeature.objects.create(
            title="Guide to Cats",
            notes="This is the guide to cats",
            superfeature_type=GUIDE_TO_ENTRY,
            parent=self.parent,
            ordering=1,
            data={
                "entries": [{
                    "title": "Cats",
                    "copy": "Everybody loves cats"
                }]
            }
        )

    def test_parent_get_children(self):
        url = reverse('super-feature-relations', kwargs={'pk': self.parent.pk})
        resp = self.api_client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, [
            OrderedDict([
                ('id', self.child.id),
                ('internal_name', None),
                ('title', 'Guide to Cats')
            ])
        ])

    def test_parent_get_children_correct_ordering(self):
        # create new children
        child2 = BaseSuperFeature.objects.create(
            title="Guide to Bats",
            notes="This is the guide to bats",
            superfeature_type=GUIDE_TO_ENTRY,
            parent=self.parent,
            ordering=2,
            data={
                "entries": [{
                    "title": "bats",
                    "copy": "Everybody loves bats"
                }]
            }
        )
        child3 = BaseSuperFeature.objects.create(
            title="Guide to Bats",
            notes="This is the guide to bats",
            superfeature_type=GUIDE_TO_ENTRY,
            parent=self.parent,
            ordering=3,
            data={
                "entries": [{
                    "title": "bats",
                    "copy": "Everybody loves bats"
                }]
            }
        )

        # switch up order
        url = reverse('super-feature-relations-ordering', kwargs={'pk': self.parent.pk})
        data = [
            {
                "id": child3.id,
                "ordering": 1
            },
            {
                "id": self.child.id,
                "ordering": 2
            },
            {
                "id": child2.id,
                "ordering": 3
            }
        ]
        resp = self.api_client.put(url, data, format="json")
        self.assertEqual(resp.status_code, 200)

        # test that the order is correct
        url = reverse('super-feature-relations', kwargs={'pk': self.parent.pk})
        resp = self.api_client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data[0]['id'], child3.id)
        self.assertEqual(resp.data[1]['id'], self.child.id)
        self.assertEqual(resp.data[2]['id'], child2.id)

    def test_parent_set_child_dates(self):
        url = reverse('super-feature-set-children-dates', kwargs={'pk': self.parent.pk})
        resp = self.api_client.put(url)

        # Will be 400 since parent publish date is not set
        self.assertEqual(resp.status_code, 400)

        self.parent.published = timezone.now()
        self.parent.save()

        url = reverse('super-feature-set-children-dates', kwargs={'pk': self.parent.pk})
        resp = self.api_client.put(url)

        # Will be 200 since parent publish date is now set
        self.assertEqual(resp.status_code, 200)

        child = BaseSuperFeature.objects.get(id=self.child.id)
        self.assertEqual(self.parent.published, child.published)

    def test_parent_set_child_dates_in_future(self):
        """Should be able to set publish dates for children even if parent
            publish date is in the future."""

        self.parent.published = timezone.now() + timedelta(days=1)
        self.parent.save()

        url = reverse(
            'super-feature-set-children-dates',
            kwargs={'pk': self.parent.pk}
        )
        resp = self.api_client.put(url)

        self.assertEqual(resp.status_code, 200)

        child = BaseSuperFeature.objects.get(id=self.child.id)
        self.assertEqual(self.parent.published, child.published)

    def test_relations_ordering(self):
        child2 = BaseSuperFeature.objects.create(
            title="Guide to Bats",
            notes="This is the guide to bats",
            superfeature_type=GUIDE_TO_ENTRY,
            parent=self.parent,
            ordering=2,
            data={
                "entries": [{
                    "title": "bats",
                    "copy": "Everybody loves bats"
                }]
            }
        )

        url = reverse('super-feature-relations-ordering', kwargs={'pk': self.parent.pk})
        data = [
            {
                "id": child2.id,
                "ordering": 1
            },
            {
                "id": self.child.id,
                "ordering": 2
            }
        ]
        resp = self.api_client.put(url, data, format="json")
        self.assertEqual(resp.status_code, 200)

        child = BaseSuperFeature.objects.get(id=self.child.id)
        child2 = BaseSuperFeature.objects.get(id=child2.id)

        # check that the ordering has been reversed
        self.assertEqual(child.ordering, 2)
        self.assertEqual(child2.ordering, 1)
