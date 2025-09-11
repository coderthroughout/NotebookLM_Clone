/**
 * API Service for Frontend-Backend Communication
 * Handles all API calls to the video production backend
 */

const API_BASE_URL = 'http://localhost:8000/api';

export interface Question {
  id: string;
  question: string;
  solution: string;
  subject: string;
  difficulty: string;
  options: string[];
  correct_answer: number;
}

export interface VideoGenerationRequest {
  question_id: string;
  question: string;
  solution: string;
}

export interface VideoGenerationResponse {
  status: string;
  question_id: string;
  message: string;
  estimated_time?: number;
  job_id?: string;
}

export interface VideoStatusResponse {
  status: string;
  question_id: string;
  progress?: number;
  current_step?: string;
  estimated_completion?: string;
  video_file?: string;
  error?: string;
}

export interface VideoPreviewResponse {
  question_id: string;
  video_file: string;
  file_size: number;
  created_at: string;
  duration?: number;
  slide_count?: number;
  script_timing?: any[];
}

export interface ApiStats {
  total_jobs: number;
  completed_jobs: number;
  failed_jobs: number;
  running_jobs: number;
  success_rate: number;
  timestamp: string;
}

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // Health check
  async checkHealth(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/health');
  }

  // Get available questions
  async getQuestions(): Promise<Question[]> {
    return this.request<Question[]>('/questions');
  }

  // Start video generation
  async generateVideo(request: VideoGenerationRequest): Promise<VideoGenerationResponse> {
    return this.request<VideoGenerationResponse>('/generate-video', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Get video generation status
  async getVideoStatus(questionId: string): Promise<VideoStatusResponse> {
    return this.request<VideoStatusResponse>(`/video-status/${questionId}`);
  }

  // Get video preview information
  async getVideoPreview(questionId: string): Promise<VideoPreviewResponse> {
    return this.request<VideoPreviewResponse>(`/video-preview/${questionId}`);
  }

  // Download video
  async downloadVideo(questionId: string): Promise<Blob> {
    const url = `${API_BASE_URL}/download-video/${questionId}`;
    
    try {
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Download failed: ${response.status} ${response.statusText}`);
      }

      return await response.blob();
    } catch (error) {
      console.error(`Video download failed for ${questionId}:`, error);
      throw error;
    }
  }

  // Get API statistics
  async getStats(): Promise<ApiStats> {
    return this.request<ApiStats>('/stats');
  }

  // Poll video status with exponential backoff
  async pollVideoStatus(
    questionId: string,
    onProgress: (status: VideoStatusResponse) => void,
    maxAttempts: number = 60, // 5 minutes with 5-second intervals
    interval: number = 5000
  ): Promise<VideoStatusResponse> {
    let attempts = 0;
    
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          attempts++;
          const status = await this.getVideoStatus(questionId);
          
          onProgress(status);
          
          if (status.status === 'completed') {
            resolve(status);
          } else if (status.status === 'failed') {
            reject(new Error(status.error || 'Video generation failed'));
          } else if (attempts >= maxAttempts) {
            reject(new Error('Video generation timeout'));
          } else {
            // Continue polling
            setTimeout(poll, interval);
          }
        } catch (error) {
          if (attempts >= maxAttempts) {
            reject(error);
          } else {
            // Retry with exponential backoff
            const backoffInterval = Math.min(interval * Math.pow(1.5, attempts), 30000);
            setTimeout(poll, backoffInterval);
          }
        }
      };
      
      poll();
    });
  }

  // Utility: Create download link for video
  createDownloadLink(questionId: string): string {
    return `${API_BASE_URL}/download-video/${questionId}`;
  }

  // Utility: Get video stream URL
  getVideoStreamUrl(questionId: string): string {
    return `${API_BASE_URL}/videos/video_${questionId}.mp4`;
  }
}

export const apiService = new ApiService();
export default apiService;
