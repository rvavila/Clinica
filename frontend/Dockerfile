# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copiar package.json e instalar dependências
COPY package*.json ./
RUN npm install

# Copiar código
COPY . .

# Build
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Instalar serve para servir a aplicação
RUN npm install -g serve

# Copiar build do stage anterior
COPY --from=builder /app/build ./build

# Expor porta
EXPOSE 3000

# Comando para rodar
CMD ["serve", "-s", "build", "-l", "3000"]
