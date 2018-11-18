import {MigrationInterface, QueryRunner} from "typeorm";

export class CommandsExecutedTypeChange1542112999117 implements MigrationInterface {

    public async up(queryRunner: QueryRunner): Promise<any> {
        await queryRunner.query(`ALTER TABLE "user" DROP COLUMN "commands_executed"`);
        await queryRunner.query(`ALTER TABLE "user" ADD "commands_executed" integer NOT NULL DEFAULT 0`);
    }

    public async down(queryRunner: QueryRunner): Promise<any> {
        await queryRunner.query(`ALTER TABLE "user" DROP COLUMN "commands_executed"`);
        await queryRunner.query(`ALTER TABLE "user" ADD "commands_executed" character varying NOT NULL DEFAULT 0`);
    }

}
