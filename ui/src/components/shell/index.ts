import { LucideIcon } from "lucide-vue-next";
import { SidebarProps } from "../ui/sidebar";

export interface NavItem {
  title: string;
  url: string;
  icon?: LucideIcon;
  isActive?: boolean;
  items?: {
    title: string;
    url: string
  }[];
};

export interface BrandingProps {
  name: string;
  logo: LucideIcon;
}

export interface UserProps {
  name: string;
  avatar?: string;
  initials: string;
}

export interface AppSidebarProps extends SidebarProps {
  nav: NavItem[];
  branding: BrandingProps;
  user?: UserProps
}

export interface AppShellProps {
  sidebar: AppSidebarProps
}
