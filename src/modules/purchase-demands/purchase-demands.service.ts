import {
  Injectable, NotFoundException, ConflictException, ForbiddenException, BadRequestException,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, In } from 'typeorm';
import { PurchaseDemandEntity } from '../../database/entities/purchase-demand.entity';
import { PurchaseDemandItemEntity } from '../../database/entities/purchase-demand-item.entity';
import { PurchaseDemandVendorEntity } from '../../database/entities/purchase-demand-vendor.entity';
import { ProjectEntity } from '../../database/entities/project.entity';
import { ItemEntity } from '../../database/entities/item.entity';
import { VendorEntity } from '../../database/entities/vendor.entity';
import { VendorBrandEntity } from '../../database/entities/vendor-brand.entity';
import { VendorGroupEntity } from '../../database/entities/vendor-group.entity';
import { VendorContactPersonEntity } from '../../database/entities/vendor-contact-person.entity';
import { SubCategoryEntity } from '../../database/entities/subcategory.entity';
import { LogEntity } from '../../database/entities/log.entity';
import { UserEntity } from '../../database/entities/user.entity';
import {
  PurchaseDemandCreateDto, PurchaseDemandUpdateDto,
  VendorAssignBodyDto, ApproveRequestDto, RejectRequestDto,
  PurchaseDemandItemInputDto,
} from './purchase-demands.dto';

const LOCKED = new Set(['approved', 'rejected', 'cancelled']);

@Injectable()
export class PurchaseDemandsService {
  constructor(
    @InjectRepository(PurchaseDemandEntity) private readonly repo: Repository<PurchaseDemandEntity>,
    @InjectRepository(PurchaseDemandItemEntity) private readonly itemRepo: Repository<PurchaseDemandItemEntity>,
    @InjectRepository(PurchaseDemandVendorEntity) private readonly vendorRepo: Repository<PurchaseDemandVendorEntity>,
    @InjectRepository(ProjectEntity) private readonly projectRepo: Repository<ProjectEntity>,
    @InjectRepository(ItemEntity) private readonly itemEntityRepo: Repository<ItemEntity>,
    @InjectRepository(VendorEntity) private readonly vendorEntityRepo: Repository<VendorEntity>,
    @InjectRepository(VendorBrandEntity) private readonly vbRepo: Repository<VendorBrandEntity>,
    @InjectRepository(VendorGroupEntity) private readonly vgRepo: Repository<VendorGroupEntity>,
    @InjectRepository(VendorContactPersonEntity) private readonly vcRepo: Repository<VendorContactPersonEntity>,
    @InjectRepository(SubCategoryEntity) private readonly scatRepo: Repository<SubCategoryEntity>,
    @InjectRepository(LogEntity) private readonly logRepo: Repository<LogEntity>,
  ) {}

  // ── Helpers ──────────────────────────────────────────────────────────────

  private async addLog(projectId: number, status: string) {
    try { await this.logRepo.save(this.logRepo.create({ project_id: projectId, status: status.slice(0, 255) })); } catch { }
  }

  private async nextCode(): Promise<string> {
    const last = await this.repo.findOne({ order: { id: 'DESC' } });
    const next = last ? last.id + 1 : 1;
    return `PD-${String(next).padStart(4, '0')}`;
  }

  private async loadDemand(id: number): Promise<PurchaseDemandEntity> {
    const demand = await this.repo.findOne({
      where: { id },
      relations: [
        'project', 'creator', 'approver',
        'items', 'items.item', 'items.item.brand', 'items.item.sub_category',
        'selected_vendors', 'selected_vendors.vendor',
      ],
    });
    if (!demand) throw new NotFoundException(`Purchase demand with id ${id} not found.`);
    return demand;
  }

  private async getSuggestedVendors(itemId: number): Promise<VendorEntity[]> { // eslint-disable-line
    const item = await this.itemEntityRepo.findOne({ where: { id: itemId } });
    if (!item) return [];
    const vendorIds = new Set<number>();
    if (item.brand_id) {
      (await this.vbRepo.find({ where: { brand_id: item.brand_id } })).forEach((v) => vendorIds.add(v.vendor_id));
    }
    if (item.scat_id) {
      const scat = await this.scatRepo.findOne({ where: { id: item.scat_id } });
      if (scat?.cat_id) {
        (await this.vgRepo.find({ where: { cat_id: scat.cat_id } })).forEach((v) => vendorIds.add(v.vendor_id));
      }
    }
    if (!vendorIds.size) return [];
    return this.vendorEntityRepo.findBy({ id: In([...vendorIds]) });
  }

  private async getVendorProfiles(item: ItemEntity): Promise<any[]> {
    const vendorIds = new Set<number>();
    if (item.brand_id) {
      (await this.vbRepo.find({ where: { brand_id: item.brand_id } })).forEach((v) => vendorIds.add(v.vendor_id));
    }
    if (item.scat_id) {
      const scat = await this.scatRepo.findOne({ where: { id: item.scat_id } });
      if (scat?.cat_id) {
        (await this.vgRepo.find({ where: { cat_id: scat.cat_id } })).forEach((v) => vendorIds.add(v.vendor_id));
      }
    }
    if (!vendorIds.size) return [];
    const vendors = await this.vendorEntityRepo.findBy({ id: In([...vendorIds]) });
    const results: any[] = [];
    for (const vendor of vendors) {
      const contact = await this.vcRepo.findOne({ where: { vendor_id: vendor.id }, order: { id: 'ASC' } });
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

  private async enrichDemand(demand: PurchaseDemandEntity) {
    const selectedVendors = await this.vendorRepo.find({
      where: { purchase_demand_id: demand.id },
      relations: ['vendor'],
      order: { id: 'ASC' },
    });

    const itemsEnriched = await Promise.all(
      demand.items.map(async (di) => {
        const suggestedVendors = await this.getSuggestedVendors(di.item_id);
        let itemBrief: any;
        if (di.item) {
          itemBrief = {
            id: di.item.id,
            brand_id: di.item.brand_id,
            brand_name: di.item.brand?.name ?? 'Generic Brand',
            scat_id: di.item.scat_id,
            scat_name: di.item.sub_category?.name ?? 'Uncategorized',
            power_rating_kv: di.item.power_rating_kv,
            voltage: di.item.voltage,
            ip_rating: di.item.ip_rating,
            uom: di.item.uom,
            purchase_rate: di.item.purchase_rate,
            sale_rate: di.item.sale_rate,
          };
        } else {
          itemBrief = {
            id: di.item_id, brand_name: 'Generic',
            scat_name: di.notes ?? `Manual Item (${di.item_id})`, uom: 'units',
          };
        }
        return {
          id: di.id,
          purchase_demand_id: di.purchase_demand_id,
          item_id: di.item_id,
          quantity: di.quantity,
          notes: di.notes,
          item: itemBrief,
          suggested_vendors: suggestedVendors.map((v) => ({
            id: v.id, name: v.name, mobile: v.mobile, email: v.email, address: v.address, vendor_type: v.type,
          })),
        };
      }),
    );

    return {
      id: demand.id,
      demand_code: demand.demand_code,
      project_id: demand.project_id,
      status: demand.status,
      remarks: demand.remarks,
      created_by: demand.created_by,
      updated_by: demand.updated_by,
      approved_by: demand.approved_by,
      approved_at: demand.approved_at,
      created_at: demand.created_at,
      updated_at: demand.updated_at,
      project: demand.project ? {
        id: demand.project.id,
        project_code: demand.project.project_code,
        name: demand.project.name,
      } : null,
      created_by_user: demand.creator ? {
        id: demand.creator.id,
        full_name: demand.creator.full_name,
        username: demand.creator.username,
      } : null,
      approved_by_user: demand.approver ? {
        id: demand.approver.id,
        full_name: demand.approver.full_name,
        username: demand.approver.username,
      } : null,
      selected_vendors: selectedVendors.map((sv) => ({
        id: sv.id,
        purchase_demand_id: sv.purchase_demand_id,
        purchase_demand_item_id: sv.purchase_demand_item_id,
        vendor_id: sv.vendor_id,
        vendor_name: sv.vendor?.name ?? null,
      })),
      items: itemsEnriched,
    };
  }

  // ── CRUD ──────────────────────────────────────────────────────────────────

  async create(dto: PurchaseDemandCreateDto, userId: number) {
    const project = await this.projectRepo.findOne({ where: { id: dto.project_id } });
    if (!project) throw new NotFoundException(`Project with id ${dto.project_id} not found.`);
    if (['completed', 'closed'].includes(project.status)) {
      throw new ConflictException(`Cannot create a purchase demand for a ${project.status} project.`);
    }
    for (const line of dto.items) {
      if (!(await this.itemEntityRepo.findOne({ where: { id: line.item_id } }))) {
        throw new NotFoundException(`Item with id ${line.item_id} not found.`);
      }
    }

    // Upsert into existing draft
    const existingDraft = await this.repo.findOne({
      where: { project_id: dto.project_id, created_by: userId, status: 'draft' },
      order: { id: 'DESC' },
      relations: ['items'],
    });

    if (existingDraft) {
      if (dto.remarks != null) existingDraft.remarks = dto.remarks;
      existingDraft.updated_by = userId;
      const existingMap = new Map(existingDraft.items.map((i) => [i.item_id, i]));
      for (const line of dto.items) {
        const existing = existingMap.get(line.item_id);
        if (existing) {
          existing.quantity = (existing.quantity ?? 0) + line.quantity;
          if (line.notes != null) existing.notes = line.notes;
          await this.itemRepo.save(existing);
        } else {
          await this.itemRepo.save(this.itemRepo.create({
            purchase_demand_id: existingDraft.id,
            item_id: line.item_id,
            quantity: line.quantity,
            notes: line.notes ?? null,
          }));
        }
      }
      await this.repo.save(existingDraft);
      const refreshed = await this.loadDemand(existingDraft.id);
      return this.enrichDemand(refreshed);
    }

    const demand = await this.repo.save(this.repo.create({
      demand_code: await this.nextCode(),
      project_id: dto.project_id,
      status: 'draft',
      remarks: dto.remarks ?? null,
      created_by: userId,
    }));

    for (const line of dto.items) {
      await this.itemRepo.save(this.itemRepo.create({
        purchase_demand_id: demand.id,
        item_id: line.item_id,
        quantity: line.quantity,
        notes: line.notes ?? null,
      }));
    }

    await this.addLog(dto.project_id, `Purchase demand ${demand.demand_code} saved`);
    const loaded = await this.loadDemand(demand.id);
    return this.enrichDemand(loaded);
  }

  async findAll(projectId: number | undefined, currentUser: UserEntity) {
    const qb = this.repo.createQueryBuilder('d')
      .leftJoinAndSelect('d.project', 'project')
      .leftJoinAndSelect('d.creator', 'creator')
      .leftJoinAndSelect('d.approver', 'approver')
      .leftJoinAndSelect('d.items', 'items')
      .leftJoinAndSelect('items.item', 'item')
      .leftJoinAndSelect('item.brand', 'brand')
      .leftJoinAndSelect('item.sub_category', 'scat')
      .orderBy('d.id', 'DESC');

    if (projectId) qb.where('d.project_id = :projectId', { projectId });

    let demands = await qb.getMany();

    if (currentUser.role === 'admin') {
      demands = demands.filter((d) => d.status === 'pending_approval' && d.creator && d.creator.role !== 'admin');
    } else if (currentUser.role === 'purchaser') {
      demands = demands.filter((d) => d.created_by === currentUser.id);
    }

    return Promise.all(demands.map((d) => this.enrichDemand(d)));
  }

  async findOne(id: number, currentUser: UserEntity) {
    const demand = await this.loadDemand(id);
    if (currentUser.role === 'admin') {
      const isNonAdminCreator = demand.creator && demand.creator.role !== 'admin';
      if (!(demand.status === 'pending_approval' && isNonAdminCreator)) {
        throw new ForbiddenException('Admins can only access submitted demands from non-admin users.');
      }
    }
    if (currentUser.role === 'purchaser' && demand.created_by !== currentUser.id) {
      throw new ForbiddenException('You can only access your own purchase demands.');
    }
    return this.enrichDemand(demand);
  }

  async update(id: number, dto: PurchaseDemandUpdateDto, currentUser: UserEntity) {
    const demand = await this.loadDemand(id);
    if (LOCKED.has(demand.status)) {
      throw new ConflictException(`Demand '${demand.demand_code}' is ${demand.status} and cannot be modified.`);
    }
    if (currentUser.role === 'purchaser' && demand.created_by !== currentUser.id) {
      throw new ForbiddenException('You can only edit your own purchase demands.');
    }
    if (dto.items) {
      for (const line of dto.items) {
        if (!(await this.itemEntityRepo.findOne({ where: { id: line.item_id } }))) {
          throw new NotFoundException(`Item with id ${line.item_id} not found.`);
        }
      }
      await this.itemRepo.delete({ purchase_demand_id: id });
      for (const line of dto.items) {
        await this.itemRepo.save(this.itemRepo.create({
          purchase_demand_id: id, item_id: line.item_id, quantity: line.quantity, notes: line.notes ?? null,
        }));
      }
    }
    if (dto.remarks != null) demand.remarks = dto.remarks;
    demand.updated_by = currentUser.id;
    await this.repo.save(demand);
    return this.enrichDemand(await this.loadDemand(id));
  }

  async addItem(demandId: number, dto: PurchaseDemandItemInputDto, currentUser: UserEntity) {
    const demand = await this.loadDemand(demandId);
    if (demand.status !== 'draft') throw new ConflictException('Items can only be added while demand is in draft status.');
    if (currentUser.role === 'purchaser' && demand.created_by !== currentUser.id) {
      throw new ForbiddenException('You can only update your own purchase demands.');
    }
    if (!(await this.itemEntityRepo.findOne({ where: { id: dto.item_id } }))) {
      throw new NotFoundException(`Item with id ${dto.item_id} not found.`);
    }
    await this.itemRepo.save(this.itemRepo.create({
      purchase_demand_id: demandId, item_id: dto.item_id, quantity: dto.quantity, notes: dto.notes ?? null,
    }));
    demand.updated_by = currentUser.id;
    await this.repo.save(demand);
    await this.addLog(demand.project_id, `Item ${dto.item_id} added to demand ${demand.demand_code}`);
    return this.enrichDemand(await this.loadDemand(demandId));
  }

  async submit(id: number, currentUser: UserEntity) {
    const demand = await this.loadDemand(id);
    if (demand.status !== 'draft') {
      throw new ConflictException(`Only draft demands can be submitted. Current status: ${demand.status}.`);
    }
    if (currentUser.role === 'purchaser' && demand.created_by !== currentUser.id) {
      throw new ForbiddenException('You can only submit your own purchase demands.');
    }
    demand.status = 'pending_approval';
    demand.updated_by = currentUser.id;
    await this.repo.save(demand);
    await this.addLog(demand.project_id, `Demand ${demand.demand_code} submitted for approval`);
    return this.enrichDemand(await this.loadDemand(id));
  }

  async getSelectedVendors(demandId: number, currentUser: UserEntity) {
    const demand = await this.loadDemand(demandId);
    if (currentUser.role === 'purchaser' && demand.created_by !== currentUser.id) {
      throw new ForbiddenException('You can only access your own purchase demands.');
    }
    const rows = await this.vendorRepo.find({
      where: { purchase_demand_id: demandId },
      relations: ['vendor'],
      order: { id: 'ASC' },
    });
    return rows.map((r) => ({
      id: r.id, purchase_demand_id: r.purchase_demand_id,
      purchase_demand_item_id: r.purchase_demand_item_id,
      vendor_id: r.vendor_id, vendor_name: r.vendor?.name ?? null,
    }));
  }

  async assignVendors(demandId: number, body: VendorAssignBodyDto, currentUser: UserEntity) {
    const demand = await this.loadDemand(demandId);
    if (!['draft', 'pending_approval'].includes(demand.status)) {
      throw new ConflictException(`Cannot select vendors when demand status is ${demand.status}.`);
    }

    await this.vendorRepo.delete({ purchase_demand_id: demandId });

    const newRows: PurchaseDemandVendorEntity[] = [];
    for (const assign of body.assignments) {
      const demandItem = await this.itemRepo.findOne({
        where: { id: assign.item_id, purchase_demand_id: demandId },
      });
      if (!demandItem) throw new BadRequestException(`Item ID ${assign.item_id} does not belong to demand ${demand.demand_code}.`);

      const itemModel = await this.itemEntityRepo.findOne({ where: { id: demandItem.item_id } });
      if (!itemModel) throw new BadRequestException(`Item ${demandItem.item_id} not found.`);
      const allowedProfiles = await this.getVendorProfiles(itemModel);
      const allowedIds = new Set(allowedProfiles.map((p) => p.vendor_id));
      const invalid = assign.vendor_ids.filter((v) => !allowedIds.has(v));
      if (invalid.length) {
        throw new BadRequestException(`Vendor IDs ${invalid.join(', ')} are not allowed for this item (Category/Brand mismatch).`);
      }

      for (const vendorId of assign.vendor_ids) {
        const row = await this.vendorRepo.save(this.vendorRepo.create({
          purchase_demand_id: demandId,
          purchase_demand_item_id: assign.item_id,
          vendor_id: vendorId,
          selected_by: currentUser.id,
        }));
        newRows.push(row);
      }
    }

    await this.addLog(demand.project_id, `Per-item vendors selected for demand ${demand.demand_code}`);
    const loaded = await this.vendorRepo.find({
      where: { purchase_demand_id: demandId },
      relations: ['vendor'],
      order: { id: 'ASC' },
    });
    return loaded.map((r) => ({
      id: r.id, purchase_demand_id: r.purchase_demand_id,
      purchase_demand_item_id: r.purchase_demand_item_id,
      vendor_id: r.vendor_id, vendor_name: r.vendor?.name ?? null,
    }));
  }

  async approve(id: number, body: ApproveRequestDto, currentUser: UserEntity) {
    const demand = await this.loadDemand(id);
    if (demand.status !== 'pending_approval') {
      throw new ConflictException(`Only pending_approval demands can be approved. Current status: ${demand.status}.`);
    }
    if (!demand.items.length) throw new ConflictException('Cannot approve an empty purchase demand.');
    const vendorCount = await this.vendorRepo.count({ where: { purchase_demand_id: id } });
    if (!vendorCount) throw new ConflictException('Select at least one vendor for this purchase demand before approval.');

    demand.status = 'approved';
    demand.approved_by = currentUser.id;
    demand.approved_at = new Date();
    if (body.remarks != null) demand.remarks = body.remarks;
    await this.repo.save(demand);
    await this.addLog(demand.project_id, `Demand ${demand.demand_code} approved`);
    return this.enrichDemand(await this.loadDemand(id));
  }

  async reject(id: number, body: RejectRequestDto, currentUser: UserEntity) {
    const demand = await this.loadDemand(id);
    if (!['pending_approval', 'draft'].includes(demand.status)) {
      throw new ConflictException(`Cannot reject a demand with status: ${demand.status}.`);
    }
    demand.status = 'rejected';
    demand.updated_by = currentUser.id;
    if (body.remarks != null) demand.remarks = body.remarks;
    await this.repo.save(demand);
    return this.enrichDemand(await this.loadDemand(id));
  }

  async cancel(id: number, currentUser: UserEntity) {
    const demand = await this.loadDemand(id);
    if (LOCKED.has(demand.status)) {
      throw new ConflictException(`Demand '${demand.demand_code}' is ${demand.status} and cannot be modified.`);
    }
    if (currentUser.role === 'purchaser' && demand.created_by !== currentUser.id) {
      throw new ForbiddenException('You can only cancel your own purchase demands.');
    }
    demand.status = 'cancelled';
    demand.updated_by = currentUser.id;
    await this.repo.save(demand);
    return this.enrichDemand(await this.loadDemand(id));
  }

  async remove(id: number) {
    const demand = await this.loadDemand(id);
    if (!['draft', 'cancelled'].includes(demand.status)) {
      throw new ConflictException('Only draft or cancelled demands can be permanently deleted.');
    }
    await this.repo.remove(demand);
  }

  async getQuotationCandidates(demandId: number) {
    const demand = await this.loadDemand(demandId);
    const vendorMap = new Map<number, any>();
    for (const di of demand.items) {
      if (!di.item) continue;
      const profiles = await this.getVendorProfiles(di.item);
      for (const profile of profiles) {
        const vid = profile.vendor_id;
        if (!vendorMap.has(vid)) vendorMap.set(vid, { ...profile, item_ids: [] });
        if (!vendorMap.get(vid).item_ids.includes(di.item_id)) {
          vendorMap.get(vid).item_ids.push(di.item_id);
        }
      }
    }
    return [...vendorMap.values()];
  }

}
