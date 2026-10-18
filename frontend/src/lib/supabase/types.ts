export type UserRole = "admin" | "user";

export type Profile = {
  id: string;
  username: string;
  display_name: string | null;
  role: UserRole;
  must_change_password: boolean;
  created_at: string;
  updated_at: string;
};

export type SavedHoroscope = {
  id: string;
  user_id: string;
  display_number: number;
  person_name: string;
  birth_date: string;
  birth_time: string;
  timezone: string;
  birthplace: string;
  latitude: number;
  longitude: number;
  ayanamsa_id: number;
  house_system_id: number;
  calculation_result: Record<string, any>;
  created_at: string;
  updated_at: string;
};

export type Database = {
  public: {
    Tables: {
      profiles: {
        Row: Profile;
        Insert: {
          id: string;
          username: string;
          display_name?: string | null;
          role?: UserRole;
          must_change_password?: boolean;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          username?: string;
          display_name?: string | null;
          role?: UserRole;
          must_change_password?: boolean;
          updated_at?: string;
        };
        Relationships: [];
      };
      saved_horoscopes: {
        Row: SavedHoroscope;
        Insert: {
          id?: string;
          user_id: string;
          display_number?: number;
          person_name: string;
          birth_date: string;
          birth_time: string;
          timezone: string;
          birthplace: string;
          latitude: number;
          longitude: number;
          ayanamsa_id: number;
          house_system_id: number;
          calculation_result: Record<string, any>;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          display_number?: number;
          person_name?: string;
          birth_date?: string;
          birth_time?: string;
          timezone?: string;
          birthplace?: string;
          latitude?: number;
          longitude?: number;
          ayanamsa_id?: number;
          house_system_id?: number;
          calculation_result?: Record<string, any>;
          updated_at?: string;
        };
        Relationships: [];
      };
    };
    Views: Record<string, never>;
    Functions: {
      is_admin: {
        Args: Record<string, never>;
        Returns: boolean;
      };
      resolve_username_to_email: {
        Args: { p_username: string };
        Returns: string;
      };
    };
    Enums: Record<string, never>;
    CompositeTypes: Record<string, never>;
  };
};
