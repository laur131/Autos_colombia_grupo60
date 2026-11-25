import { Routes } from '@angular/router';
import { authGuard } from './core/auth';

export const routes: Routes = [
  { path: 'login', loadComponent: () => import('./pages/login').then(m => m.LoginComponent) },
  {
    path: '', canActivate: [authGuard], loadComponent: () => import('./pages/shell').then(m => m.ShellComponent),
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'tablero' },
      { path: 'tablero', data: { permiso: 'tablero.ver' }, canActivate: [authGuard], loadComponent: () => import('./pages/tablero').then(m => m.TableroComponent) },
      { path: 'ingreso', data: { permiso: 'movimientos.registrar' }, canActivate: [authGuard], loadComponent: () => import('./pages/ingreso').then(m => m.IngresoComponent) },
      { path: 'historial', data: { permiso: 'historial.consultar' }, canActivate: [authGuard], loadComponent: () => import('./pages/historial').then(m => m.HistorialComponent) },
      { path: 'titulares', data: { permiso: 'titulares.gestionar' }, canActivate: [authGuard], loadComponent: () => import('./pages/titulares').then(m => m.TitularesComponent) },
      { path: 'cuentas', data: { permiso: 'usuarios.administrar' }, canActivate: [authGuard], loadComponent: () => import('./pages/cuentas').then(m => m.CuentasComponent) },
      { path: 'roles', data: { permiso: 'roles.administrar' }, canActivate: [authGuard], loadComponent: () => import('./pages/roles').then(m => m.RolesComponent) },
      { path: 'celdas', data: { permiso: 'celdas.consultar' }, canActivate: [authGuard], loadComponent: () => import('./pages/celdas').then(m => m.CeldasComponent) }
    ]
  },
  { path: '**', redirectTo: '' }
];
