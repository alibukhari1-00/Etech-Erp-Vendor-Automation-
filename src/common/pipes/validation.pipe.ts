import { ValidationPipe, UnprocessableEntityException } from '@nestjs/common';

export const globalValidationPipe = new ValidationPipe({
  whitelist: true,
  transform: true,
  exceptionFactory: (errors) => {
    const detail = errors
      .map((e) => Object.values(e.constraints ?? {}).join(', '))
      .join('; ');
    return new UnprocessableEntityException({ detail });
  },
});
