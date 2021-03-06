# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    context_unpack,
    json_view,
)
from openprocurement.auctions.core.utils import (
    apply_patch,
    opresource,
    save_auction,
)
from openprocurement.auctions.core.validation import validate_patch_auction_data
from openprocurement.auctions.dgf.views.financial.tender import FinancialAuctionResource
from openprocurement.auctions.insider.utils import check_status


@opresource(name='dgfInsider:Auction',
            path='/auctions/{auction_id}',
            auctionsprocurementMethodType="dgfInsider",
            description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#auction for more info")
class InsiderAuctionResource(FinancialAuctionResource):
    @json_view(content_type="application/json", validators=(validate_patch_auction_data,), permission='edit_auction')
    def patch(self):
        auction = self.context
        if self.request.authenticated_role != 'Administrator' and auction.status in ['complete', 'unsuccessful',
                                                                                     'cancelled']:
            self.request.errors.add('body', 'data',
                                    'Can\'t update auction in current ({}) status'.format(auction.status))
            self.request.errors.status = 403
            return
        if self.request.authenticated_role == 'chronograph' and not auction.suspended:
            apply_patch(self.request, save=False, src=self.request.validated['auction_src'])
            check_status(self.request)
            save_auction(self.request)
        else:
            apply_patch(self.request, src=self.request.validated['auction_src'])
        self.LOGGER.info('Updated auction {}'.format(auction.id),
                         extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_patch'}))
        return {'data': auction.serialize(auction.status)}