import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ProjectsController } from './projects.controller';
import { ProjectsService } from './projects.service';
import { ProjectEntity } from '../../database/entities/project.entity';
import { LocationEntity } from '../../database/entities/location.entity';
import { LogEntity } from '../../database/entities/log.entity';

@Module({
  imports: [TypeOrmModule.forFeature([ProjectEntity, LocationEntity, LogEntity])],
  controllers: [ProjectsController],
  providers: [ProjectsService],
})
export class ProjectsModule {}
