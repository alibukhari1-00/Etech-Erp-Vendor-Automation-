import {
  Injectable, NotFoundException, ConflictException,
  BadRequestException, UnprocessableEntityException,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import * as bcrypt from 'bcrypt';
import { UserEntity } from '../../database/entities/user.entity';
import { UserCreateDto, UserUpdateDto } from './users.dto';

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(UserEntity) private readonly repo: Repository<UserEntity>,
  ) {}

  async create(dto: UserCreateDto): Promise<UserEntity> {
    const existingEmail = await this.repo.findOne({ where: { email: dto.email } });
    if (existingEmail) throw new ConflictException(`A user with email '${dto.email}' already exists.`);

    const existingUsername = await this.repo.findOne({ where: { username: dto.username } });
    if (existingUsername) throw new ConflictException(`A user with username '${dto.username}' already exists.`);

    const hashed_password = await bcrypt.hash(dto.password, 10);
    const user = this.repo.create({ ...dto, hashed_password, password: undefined } as any);
    return this.repo.save(user) as unknown as Promise<UserEntity>;
  }

  async findAll(): Promise<UserEntity[]> {
    const users = await this.repo.find();
    if (!users.length) throw new NotFoundException('No users found.');
    return users;
  }

  async findOne(id: number): Promise<UserEntity> {
    if (id <= 0) throw new UnprocessableEntityException('user_id must be a positive integer.');
    const user = await this.repo.findOne({ where: { id } });
    if (!user) throw new NotFoundException(`User with id ${id} not found.`);
    return user;
  }

  async update(id: number, dto: UserUpdateDto, currentUserId: number): Promise<UserEntity> {
    if (id <= 0) throw new UnprocessableEntityException('user_id must be a positive integer.');
    const user = await this.repo.findOne({ where: { id } });
    if (!user) throw new NotFoundException(`User with id ${id} not found.`);

    if (dto.email) {
      const dup = await this.repo.findOne({ where: { email: dto.email } });
      if (dup && dup.id !== id) throw new ConflictException(`Another user with email '${dto.email}' already exists.`);
    }
    if (dto.username) {
      const dup = await this.repo.findOne({ where: { username: dto.username } });
      if (dup && dup.id !== id) throw new ConflictException(`Another user with username '${dto.username}' already exists.`);
    }

    const updateData: any = { ...dto };
    if (dto.password) {
      updateData.hashed_password = await bcrypt.hash(dto.password, 10);
    }
    delete updateData.password;

    Object.assign(user, updateData);
    return this.repo.save(user);
  }

  async remove(id: number, currentUserId: number): Promise<{ message: string }> {
    if (id <= 0) throw new UnprocessableEntityException('user_id must be a positive integer.');
    const user = await this.repo.findOne({ where: { id } });
    if (!user) throw new NotFoundException(`User with id ${id} not found.`);
    if (user.id === currentUserId) throw new BadRequestException('You cannot delete your own account.');
    await this.repo.remove(user);
    return { message: `User '${user.username}' deleted successfully.` };
  }
}
