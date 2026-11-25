import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { tap } from 'rxjs';

export const API = 'http://localhost:8000/api/v1';

export interface Sesion {
  access_token: string;
  usuario: { id: number; nombre: string; documento: string; rol: string };
  permisos: string[];
}

/** Extrae el mensaje de negocio devuelto por la API (detail.mensaje). */
export function errMsg(e: any): string {
  const d = e?.error?.detail;
  if (d?.mensaje) return `${d.mensaje}${d.codigo ? ' (' + d.codigo + ')' : ''}`;
  if (Array.isArray(d)) return 'Datos inválidos: revisa los campos del formulario';
  return e?.status === 0 ? 'No hay conexión con la API (¿está corriendo FastAPI?)' : 'Error inesperado';
}

@Injectable({ providedIn: 'root' })
export class Api {
  private http = inject(HttpClient);
  private router = inject(Router);
  sesion = signal<Sesion | null>(JSON.parse(localStorage.getItem('sesion') || 'null'));

  get token() { return this.sesion()?.access_token ?? null; }
  can(p: string) { return !!this.sesion()?.permisos.includes(p); }

  login(documento: string, password: string) {
    return this.http.post<Sesion>(`${API}/auth/login`, { documento, password }).pipe(
      tap(s => { localStorage.setItem('sesion', JSON.stringify(s)); this.sesion.set(s); }));
  }
  logout() { localStorage.removeItem('sesion'); this.sesion.set(null); this.router.navigate(['/login']); }

  private params(p?: Record<string, any>) {
    let hp = new HttpParams();
    Object.entries(p ?? {}).forEach(([k, v]) => { if (v !== null && v !== undefined && v !== '') hp = hp.set(k, String(v)); });
    return hp;
  }
  get<T>(path: string, p?: Record<string, any>) { return this.http.get<T>(API + path, { params: this.params(p) }); }
  post<T>(path: string, body: any = {}) { return this.http.post<T>(API + path, body); }
  put<T>(path: string, body: any = {}) { return this.http.put<T>(API + path, body); }
  patch<T>(path: string, body: any = {}) { return this.http.patch<T>(API + path, body); }
}
