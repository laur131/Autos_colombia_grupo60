import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { Api } from './api';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const api = inject(Api);
  const t = api.token;
  const r = t ? req.clone({ setHeaders: { Authorization: `Bearer ${t}` } }) : req;
  return next(r).pipe(catchError(e => {
    if (e.status === 401 && !req.url.endsWith('/auth/login')) api.logout();
    return throwError(() => e);
  }));
};

/** Protege rutas: exige sesión y, si la ruta declara data.permiso, que el rol lo tenga. */
export const authGuard: CanActivateFn = route => {
  const api = inject(Api), router = inject(Router);
  if (!api.token) return router.createUrlTree(['/login']);
  const p = route.data?.['permiso'];
  return !p || api.can(p) ? true : router.createUrlTree(['/']);
};
