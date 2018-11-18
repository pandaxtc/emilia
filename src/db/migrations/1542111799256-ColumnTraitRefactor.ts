import {MigrationInterface, QueryRunner} from "typeorm";

export class ColumnTraitRefactor1542111799256 implements MigrationInterface {

    public async up(queryRunner: QueryRunner): Promise<any> {
        await queryRunner.query(`ALTER TABLE "guild" ALTER COLUMN "prefix" SET DEFAULT '$'`);
        await queryRunner.query(`ALTER TABLE "guild" ALTER COLUMN "autoreply_on" SET DEFAULT false`);
        await queryRunner.query(`ALTER TABLE "user" ALTER COLUMN "commands_executed" SET DEFAULT 0`);
    }

    public async down(queryRunner: QueryRunner): Promise<any> {
        await queryRunner.query(`ALTER TABLE "user" ALTER COLUMN "commands_executed" DROP DEFAULT`);
        await queryRunner.query(`ALTER TABLE "guild" ALTER COLUMN "autoreply_on" DROP DEFAULT`);
        await queryRunner.query(`ALTER TABLE "guild" ALTER COLUMN "prefix" DROP DEFAULT`);
    }

}
