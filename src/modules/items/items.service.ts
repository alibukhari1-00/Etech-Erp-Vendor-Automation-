import { Injectable, NotFoundException, UnprocessableEntityException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, ILike, Or } from 'typeorm';
import { ItemEntity } from '../../database/entities/item.entity';
import { BrandEntity } from '../../database/entities/brand.entity';
import { SubCategoryEntity } from '../../database/entities/subcategory.entity';
import { CategoryEntity } from '../../database/entities/category.entity';
import { VendorEntity } from '../../database/entities/vendor.entity';
import { VendorBrandEntity } from '../../database/entities/vendor-brand.entity';
import { VendorGroupEntity } from '../../database/entities/vendor-group.entity';
import { VendorContactPersonEntity } from '../../database/entities/vendor-contact-person.entity';
import { ItemCreateDto } from './items.dto';

@Injectable()
export class ItemsService {
  constructor(
    @InjectRepository(ItemEntity) private readonly repo: Repository<ItemEntity>,
    @InjectRepository(BrandEntity) private readonly brandRepo: Repository<BrandEntity>,
    @InjectRepository(SubCategoryEntity) private readonly scatRepo: Repository<SubCategoryEntity>,
    @InjectRepository(CategoryEntity) private readonly catRepo: Repository<CategoryEntity>,
    @InjectRepository(VendorEntity) private readonly vendorRepo: Repository<VendorEntity>,
    @InjectRepository(VendorBrandEntity) private readonly vbRepo: Repository<VendorBrandEntity>,
    @InjectRepository(VendorGroupEntity) private readonly vgRepo: Repository<VendorGroupEntity>,
    @InjectRepository(VendorContactPersonEntity) private readonly vcRepo: Repository<VendorContactPersonEntity>,
  ) {}

  async create(dto: ItemCreateDto): Promise<ItemEntity> {
    if (!(await this.brandRepo.findOne({ where: { id: dto.brand_id } }))) {
      throw new NotFoundException(`Brand with id ${dto.brand_id} does not exist.`);
    }
    if (!(await this.scatRepo.findOne({ where: { id: dto.scat_id } }))) {
      throw new NotFoundException(`Sub-category with id ${dto.scat_id} does not exist.`);
    }
    return this.repo.save(this.repo.create(dto));
  }

  async findAll() {
    const items = await this.repo.find({ relations: ['brand', 'sub_category'] });
    if (!items.length) throw new NotFoundException('No items found.');
    return items.map((it) => ({
      ...it,
      brand_name: it.brand?.name ?? null,
      scat_name: it.sub_category?.name ?? null,
    }));
  }

  async findOne(id: number): Promise<ItemEntity> {
    if (id <= 0) throw new UnprocessableEntityException('item_id must be a positive integer.');
    const item = await this.repo.findOne({ where: { id }, relations: ['brand', 'sub_category'] });
    if (!item) throw new NotFoundException(`Item with id ${id} not found.`);
    return item;
  }

  async search(q: string, limit = 50) {
    const query = (q ?? '').trim().toLowerCase();
    if (!query) return [];

    let numeric: number | null = null;
    try { numeric = parseFloat(query.replace('kw', '').replace('kv', '').trim()); } catch { numeric = null; }
    if (numeric !== null && isNaN(numeric)) numeric = null;

    const qb = this.repo.createQueryBuilder('item')
      .innerJoin('item.brand', 'brand')
      .innerJoin('item.sub_category', 'scat')
      .innerJoin('scat.category', 'cat')
      .select([
        'item.id AS item_id',
        'brand.name AS brand',
        'cat.name AS category',
        'scat.name AS sub_category',
        'item.power_rating_kv AS power_rating_kv',
        'item.voltage AS voltage',
        'item.uom AS uom',
      ])
      .where(
        `brand.name ILIKE :q OR cat.name ILIKE :q OR scat.name ILIKE :q
         OR CAST(item.power_rating_kv AS TEXT) ILIKE :q
         OR CAST(item.voltage AS TEXT) ILIKE :q
         OR item.uom ILIKE :q OR item.ip_rating ILIKE :q`,
        { q: `%${query}%` },
      )
      .orderBy('item.id', 'DESC')
      .limit(limit);

    if (numeric !== null) {
      qb.orWhere('item.power_rating_kv = :num', { num: numeric });
    }

    return qb.getRawMany();
  }

  async getVendorsForItem(itemId: number) {
    if (itemId <= 0) throw new UnprocessableEntityException('item_id must be a positive integer.');
    const item = await this.repo.findOne({ where: { id: itemId } });
    if (!item) throw new NotFoundException(`Item with id ${itemId} not found.`);
    return this.buildVendorProfiles(item);
  }

  async update(id: number, dto: ItemCreateDto): Promise<ItemEntity> {
    const item = await this.findOne(id);
    if (!(await this.brandRepo.findOne({ where: { id: dto.brand_id } }))) {
      throw new NotFoundException(`Brand with id ${dto.brand_id} does not exist.`);
    }
    if (!(await this.scatRepo.findOne({ where: { id: dto.scat_id } }))) {
      throw new NotFoundException(`Sub-category with id ${dto.scat_id} does not exist.`);
    }
    Object.assign(item, dto);
    return this.repo.save(item);
  }

  async remove(id: number): Promise<{ message: string }> {
    const item = await this.findOne(id);
    await this.repo.remove(item);
    return { message: `Item with id ${id} deleted successfully.` };
  }

  async buildVendorProfiles(item: ItemEntity): Promise<any[]> {
    const vendorIds = new Set<number>();

    if (item.brand_id) {
      const vbs = await this.vbRepo.find({ where: { brand_id: item.brand_id } });
      vbs.forEach((vb) => vendorIds.add(vb.vendor_id));
    }
    if (item.scat_id) {
      const scat = await this.scatRepo.findOne({ where: { id: item.scat_id } });
      if (scat?.cat_id) {
        const vgs = await this.vgRepo.find({ where: { cat_id: scat.cat_id } });
        vgs.forEach((vg) => vendorIds.add(vg.vendor_id));
      }
    }

    if (!vendorIds.size) return [];

    const vendors = await this.vendorRepo.findByIds([...vendorIds]);
    const results: any[] = [];

    for (const vendor of vendors) {
      const contact = await this.vcRepo.findOne({
        where: { vendor_id: vendor.id },
        order: { id: 'ASC' },
      });
      const vgs = await this.vgRepo.find({ where: { vendor_id: vendor.id }, relations: ['category'] });
      const vbs = await this.vbRepo.find({ where: { vendor_id: vendor.id }, relations: ['brand'] });

      results.push({
        vendor_id: vendor.id,
        vendor_name: vendor.name,
        vendor_type: vendor.type,
        vendor_group: [...new Set(vgs.map((g) => g.category?.name).filter(Boolean))].sort(),
        contact_person: contact?.name ?? null,
        contact_designation: contact?.designation ?? null,
        phone: contact?.mobile ?? vendor.mobile ?? null,
        email: vendor.email,
        website: vendor.website,
        address: vendor.address,
        brands_supplied: [...new Set(vbs.map((b) => b.brand?.name).filter(Boolean))].sort(),
      });
    }
    return results;
  }
}
