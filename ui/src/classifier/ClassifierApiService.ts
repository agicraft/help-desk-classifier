import { injectable, inject } from 'inversify';
import { ApiService } from '@/core/ApiService';
import type {
  ClassificationSchemaDto,
  ClassifiedMessageDto,
  ClassifyingMessageDto,
} from './classifier-dto';

@injectable()
export class ClassifierApiService {
  public constructor(@inject(ApiService) private apiService: ApiService) {}

  public async getClassificationSchema(): Promise<ClassificationSchemaDto> {
    return this.apiService.fetch({ method: 'GET', endpoint: 'classifier/schema' });
  }

  public async classify(data: ClassifyingMessageDto): Promise<ClassifiedMessageDto> {
    return this.apiService.fetch({ method: 'POST', endpoint: 'classifier/classify', data });
  }
}
