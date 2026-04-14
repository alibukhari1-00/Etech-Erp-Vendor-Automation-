import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { ProjectEntity } from '../../database/entities/project.entity';
import { LocationEntity } from '../../database/entities/location.entity';
import { LogEntity } from '../../database/entities/log.entity';
import { ProjectCreateDto, ProjectUpdateDto } from './projects.dto';

@Injectable()
export class ProjectsService {
  constructor(
    @InjectRepository(ProjectEntity) private readonly repo: Repository<ProjectEntity>,
    @InjectRepository(LocationEntity) private readonly locRepo: Repository<LocationEntity>,
    @InjectRepository(LogEntity) private readonly logRepo: Repository<LogEntity>,
  ) {}

  private async nextCode(): Promise<string> {
    const last = await this.repo.findOne({ order: { id: 'DESC' } });
    const next = last ? last.id + 1 : 1;
    return `PRJ-${String(next).padStart(4, '0')}`;
  }

  private async addLog(projectId: number, status: string) {
    try {
      await this.logRepo.save(this.logRepo.create({ project_id: projectId, status: status.slice(0, 255) }));
    } catch { /* non-critical */ }
  }

  async create(dto: ProjectCreateDto, createdBy: number): Promise<ProjectEntity> {
    if (dto.location_id && !(await this.locRepo.findOne({ where: { id: dto.location_id } }))) {
      throw new NotFoundException(`Location with id ${dto.location_id} not found.`);
    }
    const project = this.repo.create({
      project_code: await this.nextCode(),
      name: dto.name,
      location_id: dto.location_id ?? null,
      status: dto.status ?? 'active',
      created_by: createdBy,
    });
    const saved = await this.repo.save(project);
    await this.addLog(saved.id, `Project ${saved.project_code} created`);
    return saved;
  }

  async findAll(): Promise<ProjectEntity[]> {
    return this.repo.find({ order: { id: 'DESC' } });
  }

  async findOne(id: number): Promise<ProjectEntity> {
    const project = await this.repo.findOne({ where: { id } });
    if (!project) throw new NotFoundException(`Project with id ${id} not found.`);
    return project;
  }

  async update(id: number, dto: ProjectUpdateDto): Promise<ProjectEntity> {
    const project = await this.findOne(id);
    if (dto.location_id && !(await this.locRepo.findOne({ where: { id: dto.location_id } }))) {
      throw new NotFoundException(`Location with id ${dto.location_id} not found.`);
    }
    Object.assign(project, dto);
    return this.repo.save(project);
  }

  async remove(id: number): Promise<void> {
    const project = await this.findOne(id);
    await this.repo.remove(project);
  }
}
