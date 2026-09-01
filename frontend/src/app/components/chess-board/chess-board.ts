import { Component, signal, inject, OnInit } from '@angular/core';
import { NgxChessgroundComponent } from 'ngx-chessground';
import { Chessground } from 'chessground';
import type { Api } from 'chessground/api';
import type { Key } from 'chessground/types';
import { Chess } from 'chess.js';
import {
  ChessApiService,
  ChessResponse
} from '../../services/chess-api.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-chess-board',
  standalone: true,
  imports: [NgxChessgroundComponent, CommonModule],
  templateUrl: './chess-board.html',
  styleUrl: './chess-board.css'
})
export class ChessBoard implements OnInit {

  private chess = new Chess();
  private apiService = inject(ChessApiService);

  response = signal<ChessResponse | null>(null);

  gameId = signal<string | null>(null);

  groundApi = signal<Api | null>(null);

  ngOnInit(): void {
    this.createGame();
  }

  myFn = signal<(el: HTMLElement) => Api>((el) => {

    const api = Chessground(el, {
      fen: this.chess.fen(),
      orientation: 'white',
      turnColor: 'white',

      movable: {
        free: false,
        color: 'white',
        dests: this.getDests(),

        events: {
          after: (orig, dest) => {
            this.makeMove(orig, dest);
          }
        }
      }
    });

    this.groundApi.set(api);

    return api;
  });

  private getDests(): Map<Key, Key[]> {

    const dests = new Map<Key, Key[]>();

    for (const move of this.chess.moves({ verbose: true })) {

      if (!dests.has(move.from as Key)) {
        dests.set(move.from as Key, []);
      }

      dests.get(move.from as Key)!.push(move.to as Key);
    }

    return dests;
  }

  private createGame(): void {

    this.apiService.createGame(this.chess.fen()).subscribe({

      next: (result) => {

        console.log(
          'Partie MongoDB créée :',
          result
        );

        this.gameId.set(result.game_id);
      },

      error: (error) => {

        console.error(
          'Erreur lors de la création de la partie MongoDB :',
          error
        );
      }

    });
  }

  private makeMove(orig: string, dest: string): void {

    try {

      const move = this.chess.move({
        from: orig,
        to: dest
      });

      console.log('Coup joué :', move);
      console.log('FEN :', this.chess.fen());

      const api = this.groundApi();

      if (api) {

        const nextColor =
          this.chess.turn() === 'w'
            ? 'white'
            : 'black';

        api.set({
          fen: this.chess.fen(),
          turnColor: nextColor,

          movable: {
            color: nextColor,
            dests: this.getDests()
          }
        });
      }

      const currentGameId = this.gameId();

      if (currentGameId) {

        this.apiService.addMove(
          currentGameId,
          {
            from_square: move.from,
            to_square: move.to,
            san: move.san,
            fen: this.chess.fen()
          }
        ).subscribe({

          next: (result) => {

            console.log(
              'Coup enregistré dans MongoDB :',
              result
            );

          },

          error: (error) => {

            console.error(
              'Erreur lors de l\'enregistrement du coup :',
              error
            );

          }

        });

      } else {

        console.warn(
          'Impossible d\'enregistrer le coup : gameId absent.'
        );

      }

      this.apiService.getMoves(this.chess.fen()).subscribe({

        next: (result) => {

          console.log(
            'Réponse backend :',
            result
          );

          this.response.set(result);

        },

        error: (error) => {

          console.error(
            'Erreur backend :',
            error
          );

        }

      });

    } catch (error) {

      console.log(
        'Coup illégal :',
        orig,
        '→',
        dest
      );

    }
  }
}