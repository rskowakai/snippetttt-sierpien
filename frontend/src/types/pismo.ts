export enum PismoStatus {
    NOWE = 'NOWE',
    W_ANALIZIE = 'W ANALIZIE',
    OCZEKUJE_NA_DECYZJE = 'OCZEKUJE_NA_DECYZJE',
    REALIZOWANE = 'REALIZOWANE',
    ZAKONCZONE = 'ZAKOŃCZONE',
    ANULOWANE = 'ANULOWANE',
}

export interface Pismo {
    id: number;
    owner_id: number;
    title: string;
    content: string;
    status: PismoStatus;
    user_comments?: string;
}

export interface Opcja {
    id: number;
    analiza_id: number;
    description: string;
    price: number;
    is_purchased: boolean;
}

export interface Analiza {
    id: number;
    pismo_id: number;
    summary: string;
    opcje: Opcja[];
}
