import { TestBed } from '@angular/core/testing';
import { ChessApi } from './chess-api';

describe('ChessApi', () => {
  let service: ChessApi;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ChessApi);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
