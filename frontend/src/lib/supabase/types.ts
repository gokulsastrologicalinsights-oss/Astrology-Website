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
          customer_id?: string | null;
          updated_at?: string;
        };
        Relationships: [];
      };
      customers: {
        Row: {
          id: string;
          user_id: string;
          full_name: string;
          birth_date: string;
          country_code: string;
          phone_number: string;
          normalized_phone: string;
          whatsapp_number: string;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          full_name: string;
          birth_date: string;
          country_code?: string;
          phone_number: string;
          normalized_phone: string;
          whatsapp_number: string;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          full_name?: string;
          birth_date?: string;
          country_code?: string;
          phone_number?: string;
          normalized_phone?: string;
          whatsapp_number?: string;
          updated_at?: string;
        };
        Relationships: [];
      };
      customer_birthday_wishes: {
        Row: {
          id: string;
          customer_id: string;
          wish_date: string;
          sent_by: string | null;
          sent_at: string;
        };
        Insert: {
          id?: string;
          customer_id: string;
          wish_date: string;
          sent_by?: string | null;
          sent_at?: string;
        };
        Update: {
          id?: string;
          customer_id?: string;
          wish_date?: string;
          sent_by?: string | null;
          sent_at?: string;
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
