import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { storage } from './storage';
import type { User } from '@shared/schema';

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-here';
const JWT_EXPIRES_IN = '7d';

export class AuthService {
  async hashPassword(password: string): Promise<string> {
    return bcrypt.hash(password, 10);
  }

  async verifyPassword(password: string, hashedPassword: string): Promise<boolean> {
    return bcrypt.compare(password, hashedPassword);
  }

  generateToken(user: User): string {
    return jwt.sign(
      { 
        id: user.id,
        username: user.username,
        role: user.role 
      },
      JWT_SECRET,
      { expiresIn: JWT_EXPIRES_IN }
    );
  }

  verifyToken(token: string): any {
    try {
      return jwt.verify(token, JWT_SECRET);
    } catch (error) {
      return null;
    }
  }

  async createAdminUser(): Promise<void> {
    try {
      // Check if admin user already exists
      const existingAdmin = await storage.getUserByUsername('Admin');
      if (existingAdmin) {
        console.log('Admin user already exists');
        return;
      }

      // Create admin user with the specified credentials
      const hashedPassword = await this.hashPassword('Sanku@0630');
      await storage.createUser({
        username: 'Admin',
        password: hashedPassword,
        role: 'admin',
        email: 'admin@codingteam.com',
      });

      console.log('Admin user created successfully');
    } catch (error) {
      console.error('Failed to create admin user:', error);
    }
  }

  async login(username: string, password: string): Promise<{ user: User; token: string } | null> {
    const user = await storage.getUserByUsername(username);
    if (!user) {
      return null;
    }

    const isValidPassword = await this.verifyPassword(password, user.password);
    if (!isValidPassword) {
      return null;
    }

    // Update last login
    await storage.updateUser(user.id, { lastLogin: new Date() });

    const token = this.generateToken(user);
    return { user, token };
  }

  async validateSession(token: string): Promise<User | null> {
    const payload = this.verifyToken(token);
    if (!payload) {
      return null;
    }

    const user = await storage.getUser(payload.id);
    return user && user.isActive ? user : null;
  }
}

export const authService = new AuthService();