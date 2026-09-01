import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ChessResponse {
  fen: string;

  lichess: {
    status: string;
    message?: string;
    data?: any;
  };

  stockfish: {
    status: string;
    message?: string;
    data?: any;
  };

  milvus: {
    status: string;
    message?: string;
    data?: any[];
  };

  youtube: {
    status: string;
    message?: string;
    data?: any[];
  };
}

@Injectable({
  providedIn: 'root'
})
export class ChessApiService {

  private http = inject(HttpClient);

  private readonly apiUrl = '/api/v1';

  getMoves(fen: string): Observable<ChessResponse> {
    return this.http.get<ChessResponse>(
      `${this.apiUrl}/moves/${encodeURIComponent(fen)}`
    );
  }

  createGame(initialFen: string): Observable<{ game_id: string }> {
    return this.http.post<{ game_id: string }>(
      `${this.apiUrl}/games`,
      {
        initial_fen: initialFen
      }
    );
  }

  addMove(gameId: string, moveData: any): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/games/${gameId}/moves`,
      moveData
    );
  }

  endGame(gameId: string): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/games/${gameId}/end`,
      {}
    );
  }
}