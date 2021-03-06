from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class YearSeasonListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('year seasons')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'yearseason'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        qs = model_admin.get_queryset(request)
        yy = qs.values_list('yr', 'season').distinct()
        # print yy.query
        yy = set(yy)
        yy = sorted(yy, key=lambda x: x[0])
        for y in yy:
            v = u'{}-{}'.format(y[0], y[1])
            yield (v, _(v))
        """
        return (
            ('80s', _('in the eighties')),
            ('90s', _('in the nineties')),
        )
        """

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """

        if self.value() is None:
            return

        parts = self.value().split('-')
        if len(parts) > 0:
            return queryset.filter(yr=parts[0], season=parts[1])
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == '80s':
            return queryset.filter(birthday__gte=date(1980, 1, 1),
                                    birthday__lte=date(1989, 12, 31))
        if self.value() == '90s':
            return queryset.filter(birthday__gte=date(1990, 1, 1),
                                    birthday__lte=date(1999, 12, 31))
        """
