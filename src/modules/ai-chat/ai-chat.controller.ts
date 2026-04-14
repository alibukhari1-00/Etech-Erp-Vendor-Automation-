import { Controller, Post, Body, UseGuards, Res } from '@nestjs/common';
import type { Response } from 'express';
import { AiChatService } from './ai-chat.service';
import { ChatRequestDto } from './ai-chat.dto';
import { JwtAuthGuard } from '../../common/guards/jwt-auth.guard';
import { CurrentUser } from '../../common/decorators/current-user.decorator';
import { UserEntity } from '../../database/entities/user.entity';

@Controller('ai-chat')
@UseGuards(JwtAuthGuard)
export class AiChatController {
  constructor(private readonly service: AiChatService) {}

  @Post('ask')
  ask(@Body() dto: ChatRequestDto, @CurrentUser() user: UserEntity, @Res() res: Response) {
    return this.service.streamAsk(dto, user, res);
  }
}
