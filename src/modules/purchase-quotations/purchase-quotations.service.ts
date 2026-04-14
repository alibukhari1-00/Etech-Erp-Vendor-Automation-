import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { PurchaseQuotationEntity } from '../../database/entities/purchase-quotation.entity';
import { PurchaseDemandVendorEntity } from '../../database/entities/purchase-demand-vendor.entity';
import { VendorEntity } from '../../database/entities/vendor.entity';
import { PurchaseQuotationUpdateDto } from './purchase-quotations.dto';

@Injectable()
export class PurchaseQuotationsService {
  constructor(
    @InjectRepository(PurchaseQuotationEntity) private readonly repo: Repository<PurchaseQuotationEntity>,
    @InjectRepository(PurchaseDemandVendorEntity) private readonly pdvRepo: Repository<PurchaseDemandVendorEntity>,
    @InjectRepository(VendorEntity) private readonly vendorRepo: Repository<VendorEntity>,
  ) {}

  private async enrichWithVendorName(q: PurchaseQuotationEntity) {
    const vendor = await this.vendorRepo.findOne({ where: { id: q.vendor_id } });
    return { ...q, vendor_name: vendor?.name ?? 'Unknown Vendor' };
  }

  async initiate(demandId: number): Promise<{ message: string }> {
    const assignments = await this.pdvRepo.find({ where: { purchase_demand_id: demandId } });
    let count = 0;
    for (const assign of assignments) {
      const exists = await this.repo.findOne({
        where: {
          purchase_demand_id: demandId,
          purchase_demand_item_id: assign.purchase_demand_item_id ?? undefined,
          vendor_id: assign.vendor_id,
        },
      });
      if (!exists) {
        await this.repo.save(this.repo.create({
          purchase_demand_id: demandId,
          purchase_demand_item_id: assign.purchase_demand_item_id ?? 0,
          vendor_id: assign.vendor_id,
          status: 'pending',
        }));
        count++;
      }
    }
    return { message: `Initiated ${count} quotation requests.` };
  }

  async getForDemand(demandId: number) {
    const quotes = await this.repo.find({ where: { purchase_demand_id: demandId } });
    return Promise.all(quotes.map((q) => this.enrichWithVendorName(q)));
  }

  async update(id: number, dto: PurchaseQuotationUpdateDto) {
    const quote = await this.repo.findOne({ where: { id } });
    if (!quote) throw new NotFoundException('Quotation not found');
    Object.assign(quote, dto);
    const saved = await this.repo.save(quote);
    return this.enrichWithVendorName(saved);
  }

  async select(id: number) {
    const quote = await this.repo.findOne({ where: { id } });
    if (!quote) throw new NotFoundException('Quotation not found');
    await this.repo.update(
      { purchase_demand_item_id: quote.purchase_demand_item_id },
      { status: 'rejected' },
    );
    quote.status = 'selected';
    const saved = await this.repo.save(quote);
    return this.enrichWithVendorName(saved);
  }
}
